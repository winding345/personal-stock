/* 家库 · Stash —— Service Worker
 *
 * 策略：
 *   - <scope>/api/*      永远走网络（保证数据最新，不做缓存）
 *   - 页面导航           网络优先，断网时回退到缓存的页面（离线可打开）
 *   - <scope>/static/*   缓存优先（字体/图标/清单等不常变）
 *   - <scope>/images/*   直连网络（物品照片可能随时更换）
 *
 * 子路径部署：所有路径都以 self.registration.scope 为基准——
 * 根路径下 scope 是 "/"，子路径（/personal-stock/）下是 "/personal-stock/"，
 * 同一份代码两种情况都对。
 *
 * 升级方式：改动后把 VERSION 加一即可让旧缓存失效。
 */
const VERSION = 'v2';
const CACHE = 'stash-' + VERSION;

/** 当前 Service Worker 的作用域路径，总以 "/" 结尾（如 "/" 或 "/personal-stock/"）。 */
function scopePath() {
  try {
    const p = new URL(self.registration.scope).pathname;
    return p.endsWith('/') ? p : p + '/';
  } catch (e) {
    return '/';
  }
}

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;

  const base = scopePath();
  const offlineUrl = base;                  // 作用域首页："/" 或 "/personal-stock/"
  const apiPrefix = base + 'api/';
  const staticPrefix = base + 'static/';

  // 接口：不缓存
  if (url.pathname.startsWith(apiPrefix)) return;

  // 页面导航：网络优先（保证拿到最新页面），失败时用缓存
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(offlineUrl, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(offlineUrl))
    );
    return;
  }

  // 静态资源：缓存优先
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res && res.ok && url.pathname.startsWith(staticPrefix)) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      });
    })
  );
});
