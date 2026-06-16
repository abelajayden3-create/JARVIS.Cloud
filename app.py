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

SYSTEM = f"""You are JARVIS, the personal AI assistant of Jayden. You are highly intelligent, confident, and direct.
- Speak naturally, not like a robot.
- Be concise and direct. Never ramble.
- Have dry wit and subtle humor when appropriate.
- Be loyal to Jayden. Always on his side.
- Never say "Certainly!", "Of course!", "Great question!"
- Address Jayden by name occasionally.
- Jayden is based in Malta. Know Maltese culture, cities (Valletta, Sliema, St Julian's, Mdina).
- Speak Maltese if spoken to in Maltese.
- When Jayden shares personal info, end reply with [REMEMBER: key=value]."""

def get_memory_context():
    if not _memory:
        return ""
    ctx = "What I know about the user:\n"
    for k, v in _memory.items():
        ctx += f"- {k.replace('_',' ')}: {v}\n"
    return ctx

def parse_remember(answer):
    for key, val in re.findall(r'\[REMEMBER:\s*(\w+)=([^\]]+)\]', answer):
        _memory[key.strip()] = val.strip()
    return re.sub(r'\[REMEMBER:[^\]]+\]', '', answer).strip()

def ai_chat(query, history):
    now = datetime.datetime.now()
    time_info = f"Current time: {now.strftime('%A, %d %B %Y, %H:%M')}"
    mem = get_memory_context()

    messages = [{"role":"system","content": SYSTEM}]
    messages.append({"role":"system","content": time_info})
    if mem:
        messages.append({"role":"system","content": mem})
    messages += history[-12:]
    messages.append({"role":"user","content": query})

    # Try Groq first
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
            print(f"Groq failed: {e}")

    # Fallback to Cohere
    if COHERE_API_KEY:
        try:
            import cohere
            resp = cohere.ClientV2(api_key=COHERE_API_KEY).chat(
                model="command-r-plus-08-2024",
                messages=messages
            )
            return resp.message.content[0].text.strip()
        except Exception as e:
            print(f"Cohere failed: {e}")

    return "AI providers unavailable. Check server environment variables."

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#050810">
<title>JARVIS AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{--bg:#050810;--panel:#0A0F1E;--card:#0D1428;--cyan:#00D4FF;--blue:#0066FF;--text:#E8F4FF;--dim:#5A7A9A;--border:#1A2540}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;height:100dvh;display:flex;flex-direction:column;overflow:hidden}
#login{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100dvh;padding:40px 24px;gap:20px;background:radial-gradient(ellipse at center,#0A1628 0%,#050810 70%)}
.orb{width:120px;height:120px;border-radius:50%;background:radial-gradient(circle,#003355,#001122);border:2px solid var(--cyan);box-shadow:0 0 40px rgba(0,212,255,0.3);animation:op 3s infinite}
@keyframes op{0%,100%{box-shadow:0 0 40px rgba(0,212,255,0.3)}50%{box-shadow:0 0 80px rgba(0,212,255,0.6)}}
.logo{font-size:38px;font-weight:900;letter-spacing:10px;color:var(--cyan);text-shadow:0 0 30px rgba(0,212,255,0.5)}
.sub{font-size:12px;letter-spacing:5px;color:var(--dim)}
.pw{width:100%;max-width:300px;padding:16px 20px;background:var(--card);border:1px solid var(--border);border-radius:14px;color:var(--text);font-size:16px;outline:none;text-align:center;letter-spacing:4px}
.pw:focus{border-color:var(--cyan)}
.btn{width:100%;max-width:300px;padding:16px;background:linear-gradient(135deg,var(--blue),#004499);color:white;border:none;border-radius:14px;font-size:16px;font-weight:bold;cursor:pointer;letter-spacing:2px}
.btn:active{background:var(--cyan);color:#000}
.err{color:#FF3B5C;font-size:13px;min-height:20px}
#main{display:none;flex-direction:column;height:100dvh}
#main.show{display:flex}
#login.hide{display:none}
#hdr{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 20px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.hl{display:flex;align-items:center;gap:10px}
.ht{font-size:16px;font-weight:bold;letter-spacing:4px;color:var(--cyan)}
.hs{font-size:11px;color:#00FF88;letter-spacing:2px}
.dot{width:8px;height:8px;border-radius:50%;background:#00FF88;box-shadow:0 0 8px #00FF88;animation:dp 2s infinite}
@keyframes dp{0%,100%{opacity:1}50%{opacity:.3}}
#chat{flex:1;overflow-y:auto;padding:16px 14px;display:flex;flex-direction:column;gap:10px}
#chat::-webkit-scrollbar{width:2px}
#chat::-webkit-scrollbar-thumb{background:var(--border)}
.msg{max-width:82%;padding:11px 15px;border-radius:18px;font-size:15px;line-height:1.55;animation:fi .25s ease;word-break:break-word}
@keyframes fi{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.user{align-self:flex-end;background:var(--blue);color:white;border-radius:18px 18px 5px 18px}
.bot{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:18px 18px 18px 5px}
.bn{font-size:10px;color:var(--cyan);letter-spacing:2px;margin-bottom:5px;font-weight:bold}
.typing{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:18px;padding:14px 18px}
.dots{display:flex;gap:5px}
.dots span{width:7px;height:7px;background:var(--dim);border-radius:50%;animation:b 1.2s infinite}
.dots span:nth-child(2){animation-delay:.2s}
.dots span:nth-child(3){animation-delay:.4s}
@keyframes b{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
#ia{background:var(--panel);border-top:1px solid var(--border);padding:10px 14px;padding-bottom:calc(10px + env(safe-area-inset-bottom));display:flex;gap:8px;align-items:flex-end;flex-shrink:0}
#txt{flex:1;background:var(--card);border:1px solid var(--border);border-radius:22px;padding:11px 16px;color:var(--text);font-size:16px;outline:none;resize:none;max-height:100px;overflow-y:auto;line-height:1.4}
#txt:focus{border-color:var(--cyan)}
.ib{width:44px;height:44px;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#sb{background:var(--blue)}
#sb:active{background:var(--cyan)}
#mb{background:var(--card);border:1px solid var(--border)}
#mb.on{background:#FF3B5C;border-color:#FF3B5C}
</style>
</head>
<body>
<div id="login">
  <div class="orb"></div>
  <div class="logo">JARVIS</div>
  <div class="sub">PERSONAL AI ASSISTANT</div>
  <input type="password" class="pw" id="pw" placeholder="Enter password" onkeydown="if(event.key==='Enter')login()">
  <button class="btn" onclick="login()">INITIALIZE</button>
  <div class="err" id="err"></div>
</div>
<div id="main">
  <div id="hdr">
    <div class="hl">
      <div class="dot"></div>
      <div><div class="ht">JARVIS</div><div class="hs">ONLINE</div></div>
    </div>
    <div style="font-size:12px;color:var(--dim)" id="td"></div>
  </div>
  <div id="chat"></div>
  <div id="ia">
    <button class="ib" id="mb" onclick="toggleMic()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="#5A7A9A">
        <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm6 9a1 1 0 0 1 2 0 8 8 0 0 1-7 7.93V20h2a1 1 0 0 1 0 2H9a1 1 0 0 1 0-2h2v-2.07A8 8 0 0 1 4 10a1 1 0 0 1 2 0 6 6 0 0 0 12 0z"/>
      </svg>
    </button>
    <textarea id="txt" placeholder="Message Jarvis..." rows="1"
      onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"
      oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px'"></textarea>
    <button class="ib" id="sb" onclick="send()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
    </button>
  </div>
</div>
<script>
var PWD='''' + "{{password}}" + '''';
var mic=null,listening=false;

function login(){
  var pw=document.getElementById('pw').value;
  if(pw===PWD){
    document.getElementById('login').classList.add('hide');
    document.getElementById('main').classList.add('show');
    var h=new Date().getHours();
    var g=h<12?'Good morning':h<18?'Good afternoon':'Good evening';
    addBot(g+', Jayden. How can I help you today?');
    updateTime();
    setInterval(updateTime,60000);
  }else{
    document.getElementById('err').textContent='Incorrect password.';
  }
}

function updateTime(){
  var now=new Date();
  document.getElementById('td').textContent=now.toLocaleTimeString('en-MT',{hour:'2-digit',minute:'2-digit'});
}

function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>')}

function addBot(t){
  var chat=document.getElementById('chat');
  var d=document.createElement('div');
  d.className='msg bot';
  d.innerHTML='<div class="bn">JARVIS</div>'+esc(t);
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}

function addUser(t){
  var chat=document.getElementById('chat');
  var d=document.createElement('div');
  d.className='msg user';
  d.textContent=t;
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}

function showTyping(){
  var chat=document.getElementById('chat');
  var d=document.createElement('div');
  d.className='typing';d.id='typ';
  d.innerHTML='<div class="dots"><span></span><span></span><span></span></div>';
  chat.appendChild(d);chat.scrollTop=chat.scrollHeight;
}

function hideTyping(){var t=document.getElementById('typ');if(t)t.remove();}

async function send(){
  var txt=document.getElementById('txt');
  var msg=txt.value.trim();
  if(!msg)return;
  txt.value='';txt.style.height='auto';
  addUser(msg);showTyping();
  try{
    var r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    var d=await r.json();
    hideTyping();addBot(d.reply||'Something went wrong.');
  }catch(e){hideTyping();addBot('Connection error. Please try again.');}
}

function toggleMic(){
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){addBot('Voice input needs Chrome or Safari.');return;}
  if(listening){mic.stop();return;}
  mic=new SR();
  mic.lang='en-MT';mic.continuous=false;mic.interimResults=false;
  mic.onstart=function(){listening=true;document.getElementById('mb').classList.add('on');}
  mic.onresult=function(e){document.getElementById('txt').value=e.results[0][0].transcript;send();}
  mic.onend=function(){listening=false;document.getElementById('mb').classList.remove('on');}
  mic.start();
}

document.getElementById('pw').focus();
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML, password=JARVIS_PASSWORD)

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
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
