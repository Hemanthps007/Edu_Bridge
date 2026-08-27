// StudyBridge main JS
document.querySelectorAll('[data-counter]').forEach(el=>{
  const target=parseInt(el.dataset.counter);
  const obs=new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting){
        let c=0,step=target/90;
        const t=setInterval(()=>{c+=step;if(c>=target){c=target;clearInterval(t);}el.textContent=Math.floor(c).toLocaleString();},16);
        obs.unobserve(el);
      }
    });
  });
  obs.observe(el);
});
setTimeout(()=>{const b=document.getElementById('toastBox');if(b){b.style.transition='opacity .5s';b.style.opacity='0';}},4500);
console.log('%c&#127891; StudyBridge','color:#0EA5E9;font-size:18px;font-weight:bold;');
