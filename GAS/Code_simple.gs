// ========================================
// シンプル版（iPhone対応）
// ========================================
// GITHUB_TOKEN はスクリプトプロパティに保存してください
// ========================================
const CONFIG = {
  OWNER: 'sinzy',
  REPO: 'py_timetree_scraper',
  WORKFLOW_FILE: 'main.yml',
  REF: 'main'
};

function getGitHubToken() {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) {
    throw new Error('GITHUB_TOKEN がスクリプトプロパティに設定されていません');
  }
  return token;
}

function doGet() {
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TimeTree Trigger</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: linear-gradient(135deg, #1a1a2e, #0f3460);
      color: #fff;
      padding: 20px;
    }
    .container {
      text-align: center;
      background: rgba(255,255,255,0.1);
      padding: 40px;
      border-radius: 20px;
      max-width: 400px;
      width: 100%;
    }
    .logo { font-size: 60px; margin-bottom: 10px; }
    h1 { font-size: 24px; margin-bottom: 30px; }
    #status {
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
      min-height: 80px;
    }
    .loading { background: rgba(255,193,7,0.2); }
    .success { background: rgba(0,255,136,0.2); }
    .error { background: rgba(255,82,82,0.2); }
    .icon { font-size: 40px; }
    .message { margin-top: 10px; font-size: 14px; }
    button {
      padding: 15px 30px;
      font-size: 16px;
      background: linear-gradient(135deg, #00d9ff, #00ff88);
      color: #1a1a2e;
      border: none;
      border-radius: 30px;
      font-weight: bold;
      cursor: pointer;
    }
    button:disabled { opacity: 0.5; }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">🌳</div>
    <h1>TimeTree Scraper</h1>
    <div id="status" class="loading">
      <div class="icon">⏳</div>
      <div class="message">実行中...</div>
    </div>
    <button id="btn" onclick="run()" disabled>再実行</button>
  </div>
  <script>
    function run() {
      var s = document.getElementById('status');
      var b = document.getElementById('btn');
      s.className = 'loading';
      s.innerHTML = '<div class="icon">⏳</div><div class="message">実行中...</div>';
      b.disabled = true;
      google.script.run
        .withSuccessHandler(function(r) {
          b.disabled = false;
          if (r.success) {
            s.className = 'success';
            s.innerHTML = '<div class="icon">✅</div><div class="message">' + r.message + '<br>' + r.timestamp + '</div>';
          } else {
            s.className = 'error';
            s.innerHTML = '<div class="icon">❌</div><div class="message">' + r.message + '</div>';
          }
        })
        .withFailureHandler(function(e) {
          b.disabled = false;
          s.className = 'error';
          s.innerHTML = '<div class="icon">❌</div><div class="message">' + e.message + '</div>';
        })
        .triggerWorkflow();
    }
    run();
  </script>
</body>
</html>`;
  return HtmlService.createHtmlOutput(html)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function triggerWorkflow() {
  const url = 'https://api.github.com/repos/' + CONFIG.OWNER + '/' + CONFIG.REPO + '/actions/workflows/' + CONFIG.WORKFLOW_FILE + '/dispatches';
  
  try {
    var token = getGitHubToken();
    var options = {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      payload: JSON.stringify({ ref: CONFIG.REF }),
      muteHttpExceptions: true
    };
    
    var response = UrlFetchApp.fetch(url, options);
    var statusCode = response.getResponseCode();
    
    if (statusCode === 204) {
      return {
        success: true,
        message: 'ワークフローを実行しました！',
        timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
      };
    } else {
      return {
        success: false,
        message: 'エラー (' + statusCode + '): ' + response.getContentText(),
        timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
      };
    }
  } catch (error) {
    return {
      success: false,
      message: 'エラー: ' + error.message,
      timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
    };
  }
}

