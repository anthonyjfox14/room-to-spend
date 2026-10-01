/* ══════════════════════════════════════════════════════════════════════
   The dot field — the ground the white pages sit on.

   A static ink lattice at 22px that the cursor pushes aside, the dots it
   displaces lighting periwinkle. It replaces the navy constellation on
   every page that moved to the paper system: a constellation is a thing
   you can see in the dark, and there is no dark any more.

   Lifted out of the landing (index.html, makeDotField) when the categories
   surface moved onto the same ground, so the two pages run one painter
   rather than two that drift. Mount it on a fixed, masked canvas:

     <canvas id="dotField"></canvas>
     window.mountDotField(document.getElementById('dotField'))
   ══════════════════════════════════════════════════════════════════════ */
(function(){
  var reduce = window.matchMedia &&
               window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  window.mountDotField = function(cv){
    if (!cv || !cv.getContext) return;
    var lx = cv.getContext('2d');
    var base = document.createElement('canvas'), bx = base.getContext('2d');
    var SPACING = 22, DOT = 1.05, INFLUENCE = 170, PUSH = 46;
    var BASE_RGBA = 'rgba(11,17,56,0.11)', ACCENT = '76,91,228';
    var LW = 0, LH = 0, DPR = 1;
    var ex = -9999, ey = -9999, amp = 0, raf = null;

    function build(){
      DPR = Math.min(window.devicePixelRatio || 1, 2);
      LW = window.innerWidth; LH = window.innerHeight;
      cv.width = LW * DPR; cv.height = LH * DPR;
      base.width = LW * DPR; base.height = LH * DPR;
      lx.setTransform(DPR,0,0,DPR,0,0); bx.setTransform(DPR,0,0,DPR,0,0);
      bx.clearRect(0,0,LW,LH);
      bx.fillStyle = BASE_RGBA;
      for (var y = SPACING/2; y < LH; y += SPACING)
        for (var x = SPACING/2; x < LW; x += SPACING){
          bx.beginPath(); bx.arc(x,y,DOT,0,6.283); bx.fill();
        }
      paint();
    }

    function paint(){
      /* a resize on the way out of the page can hand this a zero-size
         canvas, and drawImage throws on one */
      if (!base.width || !base.height) return;
      lx.clearRect(0,0,LW,LH);
      lx.drawImage(base,0,0,LW,LH);
      if (reduce || ex < -9000 || amp < 0.01) return;
      var R = INFLUENCE, S = PUSH * amp;
      lx.clearRect(ex-R-4, ey-R-4, R*2+8, R*2+8);
      var x0 = Math.floor((ex-R-SPACING)/SPACING)*SPACING + SPACING/2;
      var y0 = Math.floor((ey-R-SPACING)/SPACING)*SPACING + SPACING/2;
      for (var y = y0; y <= ey+R+SPACING; y += SPACING){
        if (y < 0 || y > LH) continue;
        for (var x = x0; x <= ex+R+SPACING; x += SPACING){
          if (x < 0 || x > LW) continue;
          var dx = x-ex, dy = y-ey, d = Math.sqrt(dx*dx + dy*dy);
          if (d > R){
            lx.fillStyle = BASE_RGBA;
            lx.beginPath(); lx.arc(x,y,DOT,0,6.283); lx.fill();
            continue;
          }
          if (d <= 0.001) continue;              // no bearing directly under the cursor
          var t = 1 - d/R;
          var nd = d + S*t*t;
          var nx = ex + (dx/d)*nd, ny = ey + (dy/d)*nd;
          var ring = t*t*(3-2*t);
          lx.fillStyle = 'rgba(' + ACCENT + ',' + (0.11 + ring*0.52).toFixed(3) + ')';
          lx.beginPath(); lx.arc(nx, ny, DOT + ring*0.75, 0, 6.283); lx.fill();
        }
      }
    }

    /* The void tracks the pointer 1:1. There is no eased trail and no
       strength ramp: the field is at full push on the first move, so the
       effect is simply present rather than arriving. pointermove already
       coalesces to at most one event per frame, so painting straight from
       the handler costs no more than a rAF loop would. */
    function wake(){ if (raf === null && !reduce) raf = requestAnimationFrame(fade); }
    function fade(){
      amp += (0 - amp) * 0.18;
      if (amp < 0.01){ amp = 0; paint(); raf = null; return; }
      paint();
      raf = requestAnimationFrame(fade);
    }

    window.addEventListener('pointermove', function(e){
      if (reduce) return;
      if (raf !== null){ cancelAnimationFrame(raf); raf = null; }   // cancel any fade-out
      ex = e.clientX; ey = e.clientY; amp = 1;
      paint();
    }, { passive:true });
    /* only the exit is animated, so the field does not snap off */
    window.addEventListener('pointerleave', function(){ wake(); }, { passive:true });

    var rt; window.addEventListener('resize', function(){
      clearTimeout(rt); rt = setTimeout(build, 120);
    });
    build();
  };
})();
