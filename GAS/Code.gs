// ========================================
// 設定値
// ========================================
// GITHUB_TOKEN はスクリプトプロパティに保存してください
// 設定方法：
//   1. GASエディタで「プロジェクトの設定」（歯車アイコン）をクリック
//   2. 「スクリプト プロパティ」セクションで「スクリプト プロパティを追加」
//   3. プロパティ名: GITHUB_TOKEN
//   4. 値: ghp_xxxxxxxxxxxxxxxxxxxx（あなたのトークン）
// ========================================
const CONFIG = {
  OWNER: 'sinzy',                             // GitHubユーザー名
  REPO: 'py_timetree_scraper',               // リポジトリ名
  WORKFLOW_FILE: 'main.yml',                 // ワークフローファイル名
  REF: 'main'                                // ブランチ名
};

/**
 * スクリプトプロパティからGitHub Tokenを取得
 * @returns {string} GitHub Token
 */
function getGitHubToken() {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) {
    throw new Error('GITHUB_TOKEN がスクリプトプロパティに設定されていません。プロジェクトの設定から追加してください。');
  }
  return token;
}

/**
 * HTMLページを表示
 */
function doGet() {
  // HTMLファイルから読み込む方式
  const html = HtmlService.createHtmlOutputFromFile('index')
    .setTitle('TimeTree Scraper Trigger')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
  return html;
}

/**
 * シンプルなテスト用（iPhone動作確認用）
 * URLの末尾に ?test=1 を付けるとこちらが実行される
 */
function doGetSimple() {
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>TimeTree Trigger</title>
      <style>
        body { font-family: sans-serif; padding: 20px; text-align: center; }
        .btn { padding: 20px 40px; font-size: 18px; background: #4CAF50; color: white; border: none; border-radius: 10px; }
        #result { margin-top: 20px; padding: 20px; }
      </style>
    </head>
    <body>
      <h1>TimeTree Scraper</h1>
      <p id="status">読み込み中...</p>
      <div id="result"></div>
      <script>
        google.script.run
          .withSuccessHandler(function(r) {
            document.getElementById('status').innerText = r.success ? '✅ 成功' : '❌ 失敗';
            document.getElementById('result').innerText = r.message + ' (' + r.timestamp + ')';
          })
          .withFailureHandler(function(e) {
            document.getElementById('status').innerText = '❌ エラー';
            document.getElementById('result').innerText = e.message;
          })
          .triggerWorkflow();
      </script>
    </body>
    </html>
  `;
  return HtmlService.createHtmlOutput(html)
    .setTitle('TimeTree Trigger')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/**
 * GitHub Actions ワークフローを実行
 * @returns {Object} 実行結果
 */
function triggerWorkflow() {
  const url = `https://api.github.com/repos/${CONFIG.OWNER}/${CONFIG.REPO}/actions/workflows/${CONFIG.WORKFLOW_FILE}/dispatches`;
  
  try {
    const token = getGitHubToken();
    
    const options = {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      payload: JSON.stringify({
        ref: CONFIG.REF
      }),
      muteHttpExceptions: true
    };
    
    const response = UrlFetchApp.fetch(url, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode === 204) {
      // 204 No Content = 成功
      return {
        success: true,
        message: 'ワークフローの実行をトリガーしました！',
        timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
      };
    } else {
      const responseBody = response.getContentText();
      return {
        success: false,
        message: `エラー (${statusCode}): ${responseBody}`,
        timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
      };
    }
  } catch (error) {
    return {
      success: false,
      message: `例外エラー: ${error.message}`,
      timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
    };
  }
}
