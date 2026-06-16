from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
import os, datetime, re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "jarvis-secret-2026")
CORS(app)

GROQ_API_KEY    = os.environ.get("GROQ_API_KEY", "")
COHERE_API_KEY  = os.environ.get("COHERE_API_KEY", "")
JARVIS_PASSWORD = os.environ.get("JARVIS_PASSWORD", "jarvis2026")
USERNAME        = os.environ.get("USERNAME", "Jayden")
ASSISTANT_NAME  = os.environ.get("ASSISTANT_NAME", "JARVIS")

_memory = {}

SYSTEM = ("You are JARVIS, the personal AI assistant of Jayden. "
          "Be concise, confident, witty. Never say Certainly or Of course. "
          "Jayden is based in Malta. Speak Maltese if spoken to in Maltese.")

def get_memory_context():
    if not _memory:
        return ""
    return "Known about user:\n" + "\n".join(f"- {k}: {v}" for k,v in _memory.items())

def parse_remember(answer):
    for key, val in re.findall(r'\[REMEMBER:\s*(\w+)=([^\]]+)\]', answer):
        _memory[key.strip()] = val.strip()
    return re.sub(r'\[REMEMBER:[^\]]+\]', '', answer).strip()

def ai_chat(query, history):
    now = datetime.datetime.now()
    messages = [
        {"role":"system","content": SYSTEM},
        {"role":"system","content": f"Time: {now.strftime('%A %d %B %Y %H:%M')}"},
    ]
    mem = get_memory_context()
    if mem:
        messages.append({"role":"system","content": mem})
    messages += history[-12:]
    messages.append({"role":"user","content": query})

    if GROQ_API_KEY:
        try:
            from groq import Groq
            resp = Groq(api_key=GROQ_API_KEY).chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1024,
                temperature=0.6
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq error: {e}")

    if COHERE_API_KEY:
        try:
            import cohere
            resp = cohere.ClientV2(api_key=COHERE_API_KEY).chat(
                model="command-r-plus-08-2024",
                messages=messages
            )
            return resp.message.content[0].text.strip()
        except Exception as e:
            print(f"Cohere error: {e}")

    return "AI unavailable right now."

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<meta name="theme-color" content="#050810">
<title>JARVIS AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#050810;--panel:#0A0F1E;--card:#0D1428;--cyan:#00D4FF;--blue:#0066FF;--text:#E8F4FF;--dim:#5A7A9A;--border:#1A2540}
body{background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;height:100dvh;display:flex;flex-direction:column;overflow:hidden}
#login{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100dvh;padding:40px 24px;gap:20px}
.orb{width:100px;height:100px;border-radius:50%;background:radial-gradient(circle,#003355,#001122);border:2px solid var(--cyan);box-shadow:0 0 40px rgba(0,212,255,0.4)}
.logo{font-size:36px;font-weight:900;letter-spacing:10px;color:var(--cyan)}
.sub{font-size:11px;letter-spacing:5px;color:var(--dim)}
.pw{width:100%;max-width:280px;padding:15px 20px;background:var(--card);border:1px solid var(--border);border-radius:12px;color:var(--text);font-size:16px;outline:none;text-align:center;letter-spacing:4px}
.pw:focus{border-color:var(--cyan)}
.abtn{width:100%;max-width:280px;padding:15px;background:var(--blue);color:white;border:none;border-radius:12px;font-size:15px;font-weight:bold;cursor:pointer;letter-spacing:2px}
.abtn:active{opacity:.8}
.err{color:#FF3B5C;font-size:13px;min-height:18px}
#main{display:none;flex-direction:column;height:100dvh}
#main.show{display:flex}
#login.hide{display:none}
#hdr{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 20px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.hl{display:flex;align-items:center;gap:10px}
.ht{font-size:16px;font-weight:bold;letter-spacing:4px;color:var(--cyan)}
.hs{font-size:11px;color:#00FF88;letter-spacing:2px}
.dot{width:8px;height:8px;border-radius:50%;background:#00FF88;box-shadow:0 0 8px #00FF88}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:82%;padding:11px 15px;border-radius:18px;font-size:15px;line-height:1.55;word-break:break-word}
.user{align-self:flex-end;background:var(--blue);color:white;border-radius:18px 18px 5px 18px}
.bot{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:18px 18px 18px 5px}
.bn{font-size:10px;color:var(--cyan);letter-spacing:2px;margin-bottom:4px;font-weight:bold}
.typing{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:18px;padding:14px 18px}
.dots{display:flex;gap:5px}
.dots span{width:7px;height:7px;background:var(--dim);border-radius:50%;animation:b 1.2s infinite}
.dots span:nth-child(2){animation-delay:.2s}
.dots span:nth-child(3){animation-delay:.4s}
@keyframes b{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
#ia{background:var(--panel);border-top:1px solid var(--border);padding:10px 14px;display:flex;gap:8px;align-items:center;flex-shrink:0}
#txt{flex:1;background:var(--card);border:1px solid var(--border);border-radius:22px;padding:11px 16px;color:var(--text);font-size:16px;outline:none}
#txt:focus{border-color:var(--cyan)}
#sb{width:44px;height:44px;background:var(--blue);border:none;border-radius:50%;cursor:pointer;color:white;font-size:20px}
#sb:active{background:var(--cyan)}
</style>
</head>
<body>
<div id="login">
  <div class="orb"></div>
  <div class="logo">JARVIS</div>
  <div class="sub">PERSONAL AI ASSISTANT</div>
  <input type="password" class="pw" id="pw" placeholder="Password" onkeydown="if(event.key==='Enter')login()">
  <button class="abtn" onclick="login()">INITIALIZE</button>
  <div class="err" id="err"></div>
</div>
<div id="main">
  <div id="hdr">
    <div class="hl"><div class="dot"></div><div><div class="ht">JARVIS</div><div class="hs">ONLINE</div></div></div>
    <div style="font-size:12px;color:var(--dim)" id="td"></div>
  </div>
  <div id="chat"></div>
  <div id="ia">
    <input type="text" id="txt" placeholder="Message Jarvis..." onkeydown="if(event.key==='Enter')send()">
    <button id="sb" onclick="send()">&#10148;</button>
  </div>
</div>
<script>
var PASS = "JARVIS_PASSWORD_PLACEHOLDER";

function login(){
  var pw = document.getElementById('pw').value;
  if(pw === PASS){
    document.getElementById('login').classList.add('hide');
    document.getElementById('main').classList.add('show');
    var h = new Date().getHours();
    var g = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening';
    addBot(g + ', Jayden. How can I help you today?');
    setInterval(function(){
      var n = new Date();
      document.getElementById('td').textContent = n.toLocaleTimeString('en-MT',{hour:'2-digit',minute:'2-digit'});
    }, 1000);
  } else {
    document.getElementById('err').textContent = 'Wrong password.';
  }
}

function esc(t){ return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>'); }

function addBot(t){
  var c = document.getElementById('chat');
  var d = document.createElement('div');
  d.className = 'msg bot';
  d.innerHTML = '<div class="bn">JARVIS</div>' + esc(t);
  c.appendChild(d); c.scrollTop = c.scrollHeight;
}

function addUser(t){
  var c = document.getElementById('chat');
  var d = document.createElement('div');
  d.className = 'msg user';
  d.textContent = t;
  c.appendChild(d); c.scrollTop = c.scrollHeight;
}

function showTyping(){
  var c = document.getElementById('chat');
  var d = document.createElement('div');
  d.className = 'typing'; d.id = 'typ';
  d.innerHTML = '<div class="dots"><span></span><span></span><span></span></div>';
  c.appendChild(d); c.scrollTop = c.scrollHeight;
}

function hideTyping(){ var t = document.getElementById('typ'); if(t) t.remove(); }

async function send(){
  var txt = document.getElementById('txt');
  var msg = txt.value.trim();
  if(!msg) return;
  txt.value = '';
  addUser(msg); showTyping();
  try {
    var r = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg})});
    var d = await r.json();
    hideTyping(); addBot(d.reply || 'Error.');
  } catch(e) { hideTyping(); addBot('Connection error.'); }
}

document.getElementById('pw').focus();
</script>
</body>
</html>"""

@app.route('/')
def index():
    html = HTML.replace("JARVIS_PASSWORD_PLACEHOLDER", JARVIS_PASSWORD)
    return html

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '').strip()
    if not msg:
        return jsonify({"reply": "I didn't catch that."})
    if 'history' not in session:
        session['history'] = []
    try:
        reply = ai_chat(msg, session['history'])
        reply = parse_remember(reply)
        session['history'] = (session['history'] + [
            {"role":"user","content":msg},
            {"role":"assistant","content":reply}
        ])[-20:]
        session.modified = True
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

@app.route('/health')
def health():
    return jsonify({"status":"ok","groq":bool(GROQ_API_KEY),"cohere":bool(COHERE_API_KEY)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
