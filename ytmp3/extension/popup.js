document.getElementById('open').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    const url = tab && tab.url ? tab.url : ''
    // Open converter page and pass url as query param
    const target = 'http://127.0.0.1:8000/frontend/index.html?source=' + encodeURIComponent(url)
    chrome.tabs.create({ url: target })
  } catch (e) {
    console.error(e)
  }
})

document.getElementById('convert').addEventListener('click', async () => {
  const statusEl = document.getElementById('status')
  statusEl.textContent = 'Starting...'
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    const url = tab && tab.url ? tab.url : ''
    if (!url) { statusEl.textContent = '当前标签无 URL'; return }
    const data = new FormData()
    data.append('url', url)
    data.append('format', 'mp3')
    const res = await fetch('http://127.0.0.1:8000/convert_async', { method: 'POST', body: data })
    if (!res.ok) throw new Error('服务返回 ' + res.status)
    const j = await res.json()
    const jobId = j.job_id
    statusEl.textContent = '任务已创建：' + jobId
    // Open monitor tab
    const monitor = 'http://127.0.0.1:8000/extension/monitor.html?job=' + encodeURIComponent(jobId)
    chrome.tabs.create({ url: monitor })
    // show notification
    if (chrome.notifications) {
      chrome.notifications.create(jobId, {
        type: 'basic',
        iconUrl: 'icon48.png',
        title: 'ytmp3',
        message: '任务已创建：' + jobId + '\n在监控页查看或等待下载。'
      })
    }
  } catch (e) {
    console.error(e)
    const statusEl = document.getElementById('status')
    statusEl.textContent = '错误：' + e.message
  }
})
