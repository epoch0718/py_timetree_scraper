// ========================================
// 超シンプル版 - URLにアクセスするだけで実行
// ========================================
const CONFIG = {
  OWNER: 'sinzy',
  REPO: 'py_timetree_scraper',
  WORKFLOW_FILE: 'main.yml',
  REF: 'main'
};

function doGet() {
  var result = triggerWorkflow();
  var output = result.success 
    ? '✅ 成功\n\n' + result.message + '\n' + result.timestamp
    : '❌ 失敗\n\n' + result.message + '\n' + result.timestamp;
  
  return ContentService.createTextOutput(output);
}

function triggerWorkflow() {
  var token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) {
    return { success: false, message: 'GITHUB_TOKENが未設定', timestamp: '' };
  }
  
  var url = 'https://api.github.com/repos/' + CONFIG.OWNER + '/' + CONFIG.REPO + '/actions/workflows/' + CONFIG.WORKFLOW_FILE + '/dispatches';
  
  try {
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      payload: JSON.stringify({ ref: CONFIG.REF }),
      muteHttpExceptions: true
    });
    
    var code = response.getResponseCode();
    var now = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
    
    if (code === 204) {
      return { success: true, message: 'ワークフローを実行しました！', timestamp: now };
    } else {
      return { success: false, message: 'エラー(' + code + '): ' + response.getContentText(), timestamp: now };
    }
  } catch (e) {
    return { success: false, message: 'エラー: ' + e.message, timestamp: '' };
  }
}

