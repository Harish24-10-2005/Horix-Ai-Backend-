package service

import (
	"encoding/json"
	"fmt"
	"os"
	"path"
	"strconv"
	"strings"
	"time"

	"github.com/1Panel-dev/1Panel/agent/app/dto"
	"github.com/1Panel-dev/1Panel/agent/app/model"
	"github.com/1Panel-dev/1Panel/agent/app/repo"
	"github.com/1Panel-dev/1Panel/agent/buserr"
	"github.com/1Panel-dev/1Panel/agent/constant"
	"github.com/1Panel-dev/1Panel/agent/global"
	"github.com/jinzhu/copier"
	"github.com/pkg/errors"
	"github.com/robfig/cron/v3"
)

type CronjobService struct{}

type ICronjobService interface {
	SearchWithPage(search dto.PageCronjob) (int64, interface{}, error)
	SearchRecords(search dto.SearchRecord) (int64, interface{}, error)
	Create(cronjobDto dto.CronjobOperate) error
	LoadNextHandle(spec string) ([]string, error)
	HandleOnce(id uint) error
	Update(id uint, req dto.CronjobOperate) error
	UpdateStatus(id uint, status string) error
	Delete(req dto.CronjobBatchDelete) error
	Download(down dto.CronjobDownload) (string, error)
	StartJob(cronjob *model.Cronjob, isUpdate bool) (string, error)
	CleanRecord(req dto.CronjobClean) error

	Export(req dto.OperateByIDs) (string, error)
	Import(req []dto.CronjobTrans) error
	LoadScriptOptions() []dto.ScriptOptions

	LoadInfo(req dto.OperateByID) (*dto.CronjobOperate, error)
	LoadRecordLog(req dto.OperateByID) string
}

func NewICronjobService() ICronjobService {
	return &CronjobService{}
}

func (u *CronjobService) SearchWithPage(search dto.PageCronjob) (int64, interface{}, error) {
	total, cronjobs, err := cronjobRepo.Page(search.Page, search.PageSize, repo.WithByLikeName(search.Info), repo.WithOrderRuleBy(search.OrderBy, search.Order))
	var dtoCronjobs []dto.CronjobInfo
	for _, cronjob := range cronjobs {
		var item dto.CronjobInfo
		if err := copier.Copy(&item, &cronjob); err != nil {
			return 0, nil, buserr.WithDetail("ErrStructTransform", err.Error(), nil)
		}
		record, _ := cronjobRepo.RecordFirst(cronjob.ID)
		if record.ID != 0 {
			item.LastRecordStatus = record.Status
			item.LastRecordTime = record.StartTime.Format(constant.DateTimeLayout)
		} else {
			item.LastRecordTime = "-"
		}
		item.SourceAccounts, item.DownloadAccount, _ = loadBackupNamesByID(cronjob.SourceAccountIDs, cronjob.DownloadAccountID)
		alertBase := dto.AlertBase{
			AlertType: cronjob.Type,
			EntryID:   cronjob.ID,
		}
		alertInfo, _ := alertRepo.Get(alertRepo.WithByType(alertBase.AlertType), alertRepo.WithByProject(strconv.Itoa(int(alertBase.EntryID))), repo.WithByStatus(constant.AlertEnable))
		if alertInfo.SendCount != 0 {
			item.AlertCount = alertInfo.SendCount
		} else {
			item.AlertCount = 0
		}
		if cronjob.Type == "snapshot" && len(cronjob.SnapshotRule) != 0 {
			_ = json.Unmarshal([]byte(cronjob.SnapshotRule), &item.SnapshotRule)
		}
		dtoCronjobs = append(dtoCronjobs, item)
	}
	return total, dtoCronjobs, err
}

func (u *CronjobService) LoadInfo(req dto.OperateByID) (*dto.CronjobOperate, error) {
	cronjob, err := cronjobRepo.Get(repo.WithByID(req.ID))
	var item dto.CronjobOperate
	if err := copier.Copy(&item, &cronjob); err != nil {
		return nil, buserr.WithDetail("ErrStructTransform", err.Error(), nil)
	}
	alertBase := dto.AlertBase{
		AlertType: cronjob.Type,
		EntryID:   cronjob.ID,
	}
	alertInfo, _ := alertRepo.Get(alertRepo.WithByType(alertBase.AlertType), alertRepo.WithByProject(strconv.Itoa(int(alertBase.EntryID))), repo.WithByStatus(constant.AlertEnable))
	item.AlertMethod = alertInfo.Method
	if alertInfo.SendCount != 0 {
		item.AlertCount = alertInfo.SendCount
	} else {
		item.AlertCount = 0
	}
	if cronjob.Type == "snapshot" && len(cronjob.SnapshotRule) != 0 {
		_ = json.Unmarshal([]byte(cronjob.SnapshotRule), &item.SnapshotRule)
	}
	return &item, err
}

func (u *CronjobService) Export(req dto.OperateByIDs) (string, error) {
	cronjobs, err := cronjobRepo.List(repo.WithByIDs(req.IDs))
	if err != nil {
		return "", err
	}
	var data []dto.CronjobTrans
	for _, cronjob := range cronjobs {
		item := dto.CronjobTrans{
			Name:           cronjob.Name,
			Type:           cronjob.Type,
			SpecCustom:     cronjob.SpecCustom,
			Spec:           cronjob.Spec,
			Executor:       cronjob.Executor,
			ScriptMode:     cronjob.ScriptMode,
			Script:         cronjob.Script,
			Command:        cronjob.Command,
			ContainerName:  cronjob.ContainerName,
			User:           cronjob.User,
			URL:            cronjob.URL,
			DBType:         cronjob.DBType,
			ExclusionRules: cronjob.ExclusionRules,
			IsDir:          cronjob.IsDir,
			SourceDir:      cronjob.SourceDir,
			RetainCopies:   cronjob.RetainCopies,
			RetryTimes:     cronjob.RetryTimes,
			Timeout:        cronjob.Timeout,
			IgnoreErr:      cronjob.IgnoreErr,
			Secret:         cronjob.Secret,
			SnapshotRule:   cronjob.SnapshotRule,
		}
		switch cronjob.Type {
		case "app":
			if cronjob.AppID == "all" {
				break
			}
			apps := loadAppsForJob(cronjob)
			for _, app := range apps {
				item.Apps = append(item.Apps, dto.TransHelper{Name: app.App.Key, DetailName: app.Name})
			}
		case "website":
			if cronjob.Website == "all" {
				break
			}
			websites := loadWebsForJob(cronjob)
			for _, website := range websites {
				item.Websites = append(item.Websites, website.Alias)
			}
		case "database":
			if cronjob.DBName == "all" {
				break
			}
			databases := loadDbsForJob(cronjob)
			for _, db := range databases {
				item.DBNames = append(item.DBNames, dto.TransHelper{Name: db.Database, DetailName: db.Name})
			}
		}
		item.SourceAccounts, item.DownloadAccount, _ = loadBackupNamesByID(cronjob.SourceAccountIDs, cronjob.DownloadAccountID)
		alertInfo, _ := alertRepo.Get(alertRepo.WithByType(cronjob.Type), alertRepo.WithByProject(strconv.Itoa(int(cronjob.ID))), repo.WithByStatus(constant.AlertEnable))
		if alertInfo.SendCount != 0 {
			item.AlertCount = alertInfo.SendCount
			item.AlertTitle = alertInfo.Title
			item.AlertMethod = alertInfo.Method
		} else {
			item.AlertCount = 0
		}
		data = append(data, item)
	}
	itemJson, err := json.Marshal(&data)
	if err != nil {
		return "", err
	}
	return string(itemJson), nil
}

func (u *CronjobService) Import(req []dto.CronjobTrans) error {
	for _, item := range req {
		cronjobItem, _ := cronjobRepo.Get(repo.WithByName(item.Name))
		if cronjobItem.ID != 0 {
			continue
		}
		cronjob := model.Cronjob{
			Name:           item.Name,
			Type:           item.Type,
			SpecCustom:     item.SpecCustom,
			Spec:           item.Spec,
			Executor:       item.Executor,
			ScriptMode:     item.ScriptMode,
			Script:         item.Script,
			Command:        item.Command,
			ContainerName:  item.ContainerName,
			User:           item.User,
			URL:            item.URL,
			DBType:         item.DBType,
			ExclusionRules: item.ExclusionRules,
			IsDir:          item.IsDir,
			SourceDir:      item.SourceDir,
			RetainCopies:   item.RetainCopies,
			RetryTimes:     item.RetryTimes,
			Timeout:        item.Timeout,
			IgnoreErr:      item.IgnoreErr,
			Secret:         item.Secret,
			SnapshotRule:   item.SnapshotRule,
		}
		hasNotFound := false
		switch item.Type {
		case "app":
			if len(item.Apps) == 0 {
				cronjob.AppID = "all"
				break
			}
			var appIDs []string
			for _, app := range item.Apps {
				appItem, err := appInstallRepo.LoadInstallAppByKeyAndName(app.Name, app.DetailName)
				if err != nil {
					hasNotFound = true
					continue
				}
				appIDs = append(appIDs, fmt.Sprintf("%v", appItem.ID))
			}
			cronjob.AppID = strings.Join(appIDs, ",")
		case "website":
			if len(item.Websites) == 0 {
				cronjob.Website = "all"
				break
			}
			var webIDs []string
			for _, web := range item.Websites {
				webItem, err := websiteRepo.GetFirst(websiteRepo.WithAlias(web))
				if err != nil {
					hasNotFound = true
					continue
				}
				webIDs = append(webIDs, fmt.Sprintf("%v", webItem.ID))
			}
			cronjob.Website = strings.Join(webIDs, ",")
		case "database":
			if len(item.DBNames) == 0 {
				cronjob.DBName = "all"
				break
			}
			var dbIDs []string
			if cronjob.DBType == "postgresql" {
				for _, db := range item.DBNames {
					dbItem, err := postgresqlRepo.Get(postgresqlRepo.WithByPostgresqlName(db.Name), repo.WithByName(db.DetailName))
					if err != nil {
						hasNotFound = true
						continue
					}
					dbIDs = append(dbIDs, fmt.Sprintf("%v", dbItem.ID))
				}
			} else {
				for _, db := range item.DBNames {
					dbItem, err := mysqlRepo.Get(mysqlRepo.WithByMysqlName(db.Name), repo.WithByName(db.DetailName))
					if err != nil {
						hasNotFound = true
						continue
					}
					dbIDs = append(dbIDs, fmt.Sprintf("%v", dbItem.ID))
				}
			}
			cronjob.DBName = strings.Join(dbIDs, ",")
		}
		var acIDs []string
		for _, ac := range item.SourceAccounts {
			backup, err := backupRepo.Get(repo.WithByName(ac))
			if err != nil {
				hasNotFound = true
				continue
			}
			if ac == item.DownloadAccount {
				cronjob.DownloadAccountID = backup.ID
			}
			acIDs = append(acIDs, fmt.Sprintf("%v", backup.ID))
		}
		cronjob.SourceAccountIDs = strings.Join(acIDs, ",")
		if hasNotFound {
			cronjob.Status = constant.StatusPending
		} else {
			cronjob.Status = constant.StatusDisable
		}
		if item.AlertCount != 0 {
			createAlert := dto.AlertCreate{
				Title:     item.AlertTitle,
				SendCount: item.AlertCount,
				Method:    item.AlertMethod,
				Type:      cronjob.Type,
				Project:   strconv.Itoa(int(cronjob.ID)),
				Status:    constant.AlertEnable,
			}
			_ = NewIAlertService().CreateAlert(createAlert)
		}
		_ = cronjobRepo.Create(&cronjob)
	}
	return nil
}

func (u *CronjobService) LoadScriptOptions() []dto.ScriptOptions {
	scripts, err := scriptRepo.List()
	if err != nil {
		return nil
	}
	lang, _ := settingRepo.GetValueByKey("Language")
	if len(lang) == 0 {
		lang = "en"
	}
	var options []dto.ScriptOptions
	for _, script := range scripts {
		var item dto.ScriptOptions
		item.ID = script.ID
		var translations = make(map[string]string)
		_ = json.Unmarshal([]byte(script.Name), &translations)
		if name, ok := translations[lang]; ok {
			item.Name = strings.ReplaceAll(name, " ", "_")
		} else {
			item.Name = strings.ReplaceAll(script.Name, " ", "_")
		}
		options = append(options, item)
	}
	return options
}

func (u *CronjobService) SearchRecords(search dto.SearchRecord) (int64, interface{}, error) {
	total, records, err := cronjobRepo.PageRecords(
		search.Page,
		search.PageSize,
		repo.WithByStatus(search.Status),
		cronjobRepo.WithByJobID(search.CronjobID),
		repo.WithByDate(search.StartTime, search.EndTime))
	var dtoCronjobs []dto.Record
	for _, record := range records {
		var item dto.Record
		if err := copier.Copy(&item, &record); err != nil {
			return 0, nil, buserr.WithDetail("ErrStructTransform", err.Error(), nil)
		}
		item.StartTime = record.StartTime.Format(constant.DateTimeLayout)
		dtoCronjobs = append(dtoCronjobs, item)
	}
	return total, dtoCronjobs, err
}

func (u *CronjobService) LoadNextHandle(specStr string) ([]string, error) {
	spec := cron.NewParser(cron.Minute | cron.Hour | cron.Dom | cron.Month | cron.Dow)
	now := time.Now()
	var nexts [5]string
	if strings.HasPrefix(specStr, "@every ") {
		duration := time.Minute
		if strings.HasSuffix(specStr, "s") {
			duration = time.Second
		}
		interval := strings.ReplaceAll(specStr, "@every ", "")
		interval = strings.ReplaceAll(interval, "s", "")
		interval = strings.ReplaceAll(interval, "m", "")
		durationItem, err := strconv.Atoi(interval)
		if err != nil {
			return nil, err
		}
		for i := 0; i < 5; i++ {
			nextTime := now.Add(time.Duration(durationItem) * duration)
			nexts[i] = nextTime.Format(constant.DateTimeLayout)
			now = nextTime
		}
		return nexts[:], nil
	}
	sched, err := spec.Parse(specStr)
	if err != nil {
		return nil, err
	}
	for i := 0; i < 5; i++ {
		nextTime := sched.Next(now)
		nexts[i] = nextTime.Format(constant.DateTimeLayout)
		now = nextTime
	}
	return nexts[:], nil
}

func (u *CronjobService) LoadRecordLog(req dto.OperateByID) string {
	record, err := cronjobRepo.GetRecord(repo.WithByID(req.ID))
	if err != nil {
		return ""
	}
	if _, err := os.Stat(record.Records); err != nil {
		return ""
	}
	content, err := os.ReadFile(record.Records)
	if err != nil {
		return ""
	}
	return string(content)
}

func (u *CronjobService) CleanRecord(req dto.CronjobClean) error {
	cronjob, err := cronjobRepo.Get(repo.WithByID(req.CronjobID))
	if err != nil {
		return err
	}
	if req.CleanData {
		if hasBackup(cronjob.Type) {
			accountMap, err := NewBackupClientMap(strings.Split(cronjob.SourceAccountIDs, ","))
			if err != nil {
				return err
			}
			if !req.CleanRemoteData {
				for key := range accountMap {
					if key != constant.Local {
						delete(accountMap, key)
					}
				}
			}
			cronjob.RetainCopies = 0
			if len(accountMap) != 0 {
				u.removeExpiredBackup(cronjob, accountMap, model.BackupRecord{})
			}
		}
	}
	if req.IsDelete {
		records, _ := backupRepo.ListRecord(backupRepo.WithByCronID(cronjob.ID))
		for _, records := range records {
			records.CronjobID = 0
			_ = backupRepo.UpdateRecord(&records)
		}
	}
	delRecords, err := cronjobRepo.ListRecord(cronjobRepo.WithByJobID(int(req.CronjobID)))
	if err != nil {
		return err
	}
	for _, del := range delRecords {
		_ = os.RemoveAll(del.Records)
	}
	if err := cronjobRepo.DeleteRecord(cronjobRepo.WithByJobID(int(req.CronjobID))); err != nil {
		return err
	}
	return nil
}

func (u *CronjobService) Download(req dto.CronjobDownload) (string, error) {
	record, _ := cronjobRepo.GetRecord(repo.WithByID(req.RecordID))
	if record.ID == 0 {
		return "", buserr.New("ErrRecordNotFound")
	}
	account, client, err := NewBackupClientWithID(req.BackupAccountID)
	if err != nil {
		return "", err
	}
	if account.Type == "LOCAL" || record.FromLocal {
		if _, err := os.Stat(record.File); err != nil && os.IsNotExist(err) {
			return "", err
		}
		return record.File, nil
	}
	tempPath := fmt.Sprintf("%s/download/%s", global.Dir.DataDir, record.File)
	if _, err := os.Stat(tempPath); err != nil && os.IsNotExist(err) {
		_ = os.MkdirAll(path.Dir(tempPath), os.ModePerm)
		isOK, err := client.Download(record.File, tempPath)
		if !isOK || err != nil {
			return "", err
		}
	}
	return tempPath, nil
}

func (u *CronjobService) HandleOnce(id uint) error {
	cronjob, _ := cronjobRepo.Get(repo.WithByID(id))
	if cronjob.ID == 0 {
		return buserr.New("ErrRecordNotFound")
	}
	u.HandleJob(&cronjob)
	return nil
}

func (u *CronjobService) Create(req dto.CronjobOperate) error {
	cronjob, _ := cronjobRepo.Get(repo.WithByName(req.Name))
	if cronjob.ID != 0 {
		return buserr.New("ErrRecordExist")
	}
	cronjob.Secret = req.Secret
	if err := copier.Copy(&cronjob, &req); err != nil {
		return buserr.WithDetail("ErrStructTransform", err.Error(), nil)
	}
	if cronjob.Type == "snapshot" {
		rule, err := json.Marshal(req.SnapshotRule)
		if err != nil {
			return err
		}
		cronjob.SnapshotRule = string(rule)
	}
	if cronjob.Type == "cutWebsiteLog" {
		backupAccount, err := backupRepo.Get(repo.WithByType(constant.Local))
		if backupAccount.ID == 0 {
			return fmt.Errorf("load local backup dir failed, err: %v", err)
		}
		cronjob.DownloadAccountID, cronjob.SourceAccountIDs = backupAccount.ID, fmt.Sprintf("%v", backupAccount.ID)
	}
	cronjob.Status = constant.StatusEnable

	global.LOG.Infof("create cronjob %s successful, spec: %s", cronjob.Name, cronjob.Spec)
	spec := cronjob.Spec
	entryIDs, err := u.StartJob(&cronjob, false)
	if err != nil {
		return err
	}
	cronjob.Spec = spec
	cronjob.EntryIDs = entryIDs
	if err := cronjobRepo.Create(&cronjob); err != nil {
		return err
	}
	if req.AlertCount != 0 {
		createAlert := dto.AlertCreate{
			Title:     req.AlertTitle,
			SendCount: req.AlertCount,
			Method:    req.AlertMethod,
			Type:      cronjob.Type,
			Project:   strconv.Itoa(int(cronjob.ID)),
			Status:    constant.AlertEnable,
		}
		err := NewIAlertService().CreateAlert(createAlert)
		if err != nil {
			return err
		}
	}
	return nil
}

func (u *CronjobService) StartJob(cronjob *model.Cronjob, isUpdate bool) (string, error) {
	if len(cronjob.EntryIDs) != 0 && isUpdate {
		ids := strings.Split(cronjob.EntryIDs, ",")
		for _, id := range ids {
			idItem, _ := strconv.Atoi(id)
			global.Cron.Remove(cron.EntryID(idItem))
		}
	}
	specs := strings.Split(cronjob.Spec, ",")
	var ids []string
	for _, spec := range specs {
		cronjob.Spec = spec
		entryID, err := u.AddCronJob(cronjob)
		if err != nil {
			return "", err
		}
		ids = append(ids, fmt.Sprintf("%v", entryID))
	}
	return strings.Join(ids, ","), nil
}

func (u *CronjobService) Delete(req dto.CronjobBatchDelete) error {
	for _, id := range req.IDs {
		cronjob, _ := cronjobRepo.Get(repo.WithByID(id))
		if cronjob.ID == 0 {
			return errors.New("find cronjob in db failed")
		}
		_ = os.RemoveAll(path.Join(global.Dir.DataDir, "task/shell", cronjob.Name))
		ids := strings.Split(cronjob.EntryIDs, ",")
		for _, id := range ids {
			idItem, _ := strconv.Atoi(id)
			global.Cron.Remove(cron.EntryID(idItem))
		}
		global.LOG.Infof("stop cronjob entryID: %s", cronjob.EntryIDs)
		if err := u.CleanRecord(dto.CronjobClean{CronjobID: id, CleanData: req.CleanData, CleanRemoteData: req.CleanRemoteData, IsDelete: true}); err != nil {
			return err
		}
		if err := cronjobRepo.Delete(repo.WithByID(id)); err != nil {
			return err
		}
		err := alertRepo.Delete(alertRepo.WithByProject(strconv.Itoa(int(cronjob.ID))), alertRepo.WithByType(cronjob.Type))
		if err != nil {
			return err
		}
	}

	return nil
}

func (u *CronjobService) Update(id uint, req dto.CronjobOperate) error {
	var cronjob model.Cronjob
	if err := copier.Copy(&cronjob, &req); err != nil {
		return buserr.WithDetail("ErrStructTransform", err.Error(), nil)
	}
	if req.Type == "snapshot" {
		itemRule, err := json.Marshal(req.SnapshotRule)
		if err != nil {
			return err
		}
		cronjob.SnapshotRule = string(itemRule)
	}
	cronModel, err := cronjobRepo.Get(repo.WithByID(id))
	if err != nil {
		return buserr.New("ErrRecordNotFound")
	}
	upMap := make(map[string]interface{})
	cronjob.EntryIDs = cronModel.EntryIDs
	cronjob.Type = cronModel.Type
	spec := cronjob.Spec
	if cronModel.Status == constant.StatusEnable {
		newEntryIDs, err := u.StartJob(&cronjob, true)
		if err != nil {
			return err
		}
		upMap["entry_ids"] = newEntryIDs
	} else {
		ids := strings.Split(cronjob.EntryIDs, ",")
		for _, id := range ids {
			idItem, _ := strconv.Atoi(id)
			global.Cron.Remove(cron.EntryID(idItem))
		}
	}

	if cronModel.Status == constant.StatusPending {
		upMap["status"] = constant.StatusEnable
	}
	upMap["name"] = req.Name
	upMap["spec_custom"] = req.SpecCustom
	upMap["spec"] = spec
	upMap["script"] = req.Script
	upMap["script_mode"] = req.ScriptMode
	upMap["command"] = req.Command
	upMap["container_name"] = req.ContainerName
	upMap["executor"] = req.Executor
	upMap["user"] = req.User

	upMap["script_id"] = req.ScriptID
	upMap["app_id"] = req.AppID
	upMap["website"] = req.Website
	upMap["exclusion_rules"] = req.ExclusionRules
	upMap["db_type"] = req.DBType
	upMap["db_name"] = req.DBName
	upMap["url"] = req.URL
	upMap["is_dir"] = req.IsDir
	upMap["source_dir"] = req.SourceDir
	upMap["snapshot_rule"] = cronjob.SnapshotRule

	upMap["source_account_ids"] = req.SourceAccountIDs
	upMap["download_account_id"] = req.DownloadAccountID
	upMap["retain_copies"] = req.RetainCopies
	upMap["retry_times"] = req.RetryTimes
	upMap["timeout"] = req.Timeout
	upMap["ignore_err"] = req.IgnoreErr
	upMap["secret"] = req.Secret
	err = cronjobRepo.Update(id, upMap)
	if err != nil {
		return err
	}
	updateAlert := dto.AlertCreate{
		Title:     req.AlertTitle,
		SendCount: req.AlertCount,
		Method:    req.AlertMethod,
		Type:      cronjob.Type,
		Project:   strconv.Itoa(int(cronModel.ID)),
	}
	err = NewIAlertService().ExternalUpdateAlert(updateAlert)
	if err != nil {
		return err
	}
	return nil
}

func (u *CronjobService) UpdateStatus(id uint, status string) error {
	cronjob, _ := cronjobRepo.Get(repo.WithByID(id))
	if cronjob.ID == 0 {
		return errors.WithMessage(buserr.New("ErrRecordNotFound"), "record not found")
	}
	var (
		entryIDs string
		err      error
	)

	if status == constant.StatusEnable {
		entryIDs, err = u.StartJob(&cronjob, false)
		if err != nil {
			return err
		}
	} else {
		ids := strings.Split(cronjob.EntryIDs, ",")
		for _, id := range ids {
			idItem, _ := strconv.Atoi(id)
			global.Cron.Remove(cron.EntryID(idItem))
		}
		global.LOG.Infof("stop cronjob entryID: %s", cronjob.EntryIDs)
	}
	return cronjobRepo.Update(cronjob.ID, map[string]interface{}{"status": status, "entry_ids": entryIDs})
}

func (u *CronjobService) AddCronJob(cronjob *model.Cronjob) (int, error) {
	addFunc := func() {
		u.HandleJob(cronjob)
	}
	global.LOG.Infof("add %s job %s successful", cronjob.Type, cronjob.Name)
	entryID, err := global.Cron.AddFunc(cronjob.Spec, addFunc)
	if err != nil {
		return 0, err
	}
	global.LOG.Infof("start cronjob entryID: %d", entryID)
	return int(entryID), nil
}
