/* メカとら Cookie 同意バナー（軽量・依存なし） */
(function () {
  var KEY = 'mechatora_cookie_consent';
  try { if (localStorage.getItem(KEY)) return; } catch (e) { return; }

  function build() {
    var bar = document.createElement('div');
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', 'Cookie同意');
    bar.style.cssText = [
      'position:fixed', 'left:16px', 'right:16px', 'bottom:16px', 'z-index:9999',
      'max-width:920px', 'margin:0 auto', 'background:#1f2937', 'color:#fff',
      'border-radius:12px', 'box-shadow:0 10px 30px rgba(0,0,0,.25)',
      'padding:16px 18px', 'display:flex', 'flex-wrap:wrap', 'align-items:center',
      'gap:12px', 'font-size:14px', 'line-height:1.6'
    ].join(';');
    var msg = document.createElement('div');
    msg.style.cssText = 'flex:1 1 260px;min-width:220px';
    msg.innerHTML = '当サイトは、利便性向上・アクセス解析・広告配信のためにCookieを使用します。詳しくは<a href="/privacy-policy.html" style="color:#ffb04d;text-decoration:underline;">プライバシーポリシー</a>をご覧ください。';
    var btns = document.createElement('div');
    btns.style.cssText = 'display:flex;gap:8px;flex:0 0 auto';
    function mk(label, primary) {
      var b = document.createElement('button');
      b.textContent = label;
      b.style.cssText = 'cursor:pointer;border:0;border-radius:8px;padding:9px 16px;font-weight:700;font-size:14px;' +
        (primary ? 'background:#ff8c00;color:#fff;' : 'background:#374151;color:#e5e7eb;');
      return b;
    }
    var ok = mk('同意する', true);
    var no = mk('拒否', false);
    function close(v) { try { localStorage.setItem(KEY, v); } catch (e) {} bar.remove(); }
    ok.addEventListener('click', function () { close('accepted'); });
    no.addEventListener('click', function () { close('declined'); });
    btns.appendChild(no); btns.appendChild(ok);
    bar.appendChild(msg); bar.appendChild(btns);
    document.body.appendChild(bar);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
