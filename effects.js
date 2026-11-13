/* PoE Build Notifier v0.5.2 — ambient particles, cursor glow, accessibility */
(()=>{
"use strict";
const reduce=window.matchMedia("(prefers-reduced-motion: reduce)");
const root=document.querySelector("#app")||document.body;
const canvas=document.querySelector("#ember-field");
const glow=document.querySelector("#spotlight, .site-spotlight");
const themeButton=document.querySelector("body:not(.fancy-home) #theme-toggle");
const navButton=document.getElementById("mobile-menu-toggle");
if(navButton){
  navButton.addEventListener("click",()=>{
    const menu=document.getElementById("site-nav");
    const open=navButton.getAttribute("aria-expanded")!=="true";
    navButton.setAttribute("aria-expanded",String(open));
    if(menu) menu.classList.toggle("menu-open",open);
  });
}
if(themeButton){
  let theme="dark";
  try{const stored=localStorage.getItem("poe-design-theme");if(stored==="light")theme="light";}catch(_){}
  function apply(value){
    document.body.classList.toggle("light",value==="light");
    document.body.classList.toggle("dark",value==="dark");
    themeButton.textContent=value==="light"?"🌙":"☀️";
    themeButton.setAttribute("aria-label",value==="light"?"Switch to dark theme / Przełącz na ciemny":"Switch to light theme / Przełącz na jasny");
    themeButton.title=value==="light"?"Dark mode / Ciemny motyw":"Light mode / Jasny motyw";
    try{localStorage.setItem("poe-design-theme",value);}catch(_){}
  }
  apply(theme);
  themeButton.addEventListener("click",()=>apply(document.body.classList.contains("light")?"dark":"light"));
}
if(glow && !reduce.matches && window.matchMedia("(pointer:fine)").matches){
  let queued=false, px=0,py=0;
  window.addEventListener("pointermove",e=>{
    px=e.clientX;py=e.clientY;
    if(queued)return;
    queued=true;
    requestAnimationFrame(()=>{
      queued=false;
      if(glow.classList.contains("site-spotlight")){
        glow.style.setProperty("--mx",px+"px");
        glow.style.setProperty("--my",py+"px");
      }
    });
  },{passive:true});
}
if(!canvas || !canvas.getContext) return;
const context=canvas.getContext("2d",{alpha:true});
if(!context)return;
let w=0,h=0,dpr=1,particles=[],raf=0,last=0,active=true;
const mobile=window.matchMedia("(max-width: 720px)");
function resize(){
  const r=canvas.getBoundingClientRect();
  w=Math.max(1,r.width);h=Math.max(1,r.height);
  dpr=Math.min(window.devicePixelRatio||1,1.75);
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
  context.setTransform(dpr,0,0,dpr,0,0);
  const count=Math.min(mobile.matches?32:72,Math.max(18,Math.floor(w*h/24000)));
  particles=Array.from({length:count},()=>({
    x:Math.random()*w,y:Math.random()*h,
    r:.5+Math.random()*1.35,vx:(Math.random()-.5)*.13,
    vy:-(.09+Math.random()*.24),phase:Math.random()*6.28,
    a:.15+Math.random()*.44
  }));
  draw(true);
}
function draw(frozen=false){
  context.clearRect(0,0,w,h);
  const light=document.body.classList.contains("light");
  for(const p of particles){
    if(!frozen){
      p.x+=p.vx;p.y+=p.vy;p.phase+=.014;
      if(p.y<-10){p.y=h+10;p.x=Math.random()*w}
      if(p.x<-10)p.x=w+10;if(p.x>w+10)p.x=-10;
    }
    const alpha=p.a*(.75+.25*Math.sin(p.phase));
    context.fillStyle=light?"rgba(151,99,49,"+alpha+")":"rgba(244,192,113,"+alpha+")";
    context.beginPath();context.arc(p.x,p.y,p.r,0,Math.PI*2);context.fill();
  }
}
function loop(t){
 if(!active||reduce.matches){raf=0;return;}
 if(t-last>32){draw();last=t;}
 raf=requestAnimationFrame(loop);
}
function schedule(){
 cancelAnimationFrame(raf);raf=0;
 active=!document.hidden&&!reduce.matches;
 if(active)raf=requestAnimationFrame(loop);
 else draw(true);
}
const obs=new ResizeObserver(resize);obs.observe(canvas);
document.addEventListener("visibilitychange",schedule);
if(reduce.addEventListener)reduce.addEventListener("change",schedule);
resize();schedule();
})();