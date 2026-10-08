// The same-life maths, shared by the page (index.html) and the build checks (check_site.mjs).
// Reads window.RTS from data.js. Exposes window.RTSCore in the browser and module.exports in node.
(function(root){
  // fixed points inside the five spending bands, in dollars a day adjusted to buy the same everywhere
  var PTS = [7, 24, 64, 108, 200].map(function(v){ return v * 365; });

  // the twelve spending shares of someone at standard of living x, read between the band points on a log scale
  function weights(k, x){
    var b = []; k.w.forEach(function(v, i){ if (v) b.push([PTS[i], v]); });
    var n = b.length;
    if (x <= b[0][0]) return b[0][1];
    if (x >= b[n-1][0]) return b[n-1][1];
    for (var i = 0; i < n - 1; i++){
      if (x <= b[i+1][0]){
        var t = (Math.log(x) - Math.log(b[i][0])) / (Math.log(b[i+1][0]) - Math.log(b[i][0]));
        return b[i][1].map(function(v, j){ return v + (b[i+1][1][j] - v) * t; });
      }
    }
  }
  function topPoint(k){ var t = 0; k.w.forEach(function(v, i){ if (v) t = PTS[i]; }); return t; }

  // a city's prices: its country's, scaled by the city's own. Within a country every city difference counts. Across
  // borders a city's prices for things other than rent count only when both cities have official figures for them
  // (US metros, Japanese prefectures, UK regions, Canadian cities); otherwise only rent differs, so the two cities are
  // compared on the same basis.
  function prices(K, city, keepAll){
    var k = K[city.c]; if (!city.m) return k.p;
    return k.p.map(function(v, j){ return v * (keepAll || j === 3 ? city.m[j] : 1); });
  }
  // how much the same life costs in B against A: a Fisher index, the geometric mean of the price change on A's basket
  // and on B's basket, both for someone at standard of living x
  function costRatio(K, a, b, x){
    var keepAll = a.c === b.c || (a.full && b.full);
    var A = K[a.c], B = K[b.c], pa = prices(K, a, keepAll), pb2 = prices(K, b, keepAll);
    var wa = weights(A, x), wb = weights(B, x), L = 0, la = 0, P = 0, pb = 0;
    for (var j = 0; j < 12; j++){
      var rel = pb2[j] / pa[j];
      L += wa[j] * rel; la += wa[j];
      P += wb[j] / rel; pb += wb[j];
    }
    return Math.sqrt((L / la) * (pb / P));
  }

  // how far the answer could be off, as a standard error on the log of the ratio (see README, "How sure").
  // The parts are independent, so they add in squares:
  //  - each country's price level, across borders only (ICP 2021 carried to 2026): D.unc.country[cc]
  //  - each city's rent against its country, by where the rent comes from (src), times the housing share
  //  - each city's other prices: the error of its official figures when they count (D.unc.own); when it has none,
  //    the typical city spread (D.unc.other); when it has them but they are dropped across a border, their own
  //    known effect on the answer, so the route between two cities stays inside the range
  function ownEffect(K, c, x){
    var nat = {n: '', c: c.c, m: null}, rentOnly = {n: c.n, c: c.c, m: c.m.map(function(v, j){ return j === 3 ? v : 1; })};
    return Math.abs(Math.log(costRatio(K, nat, c, x) / costRatio(K, nat, rentOnly, x)));
  }
  function logError(D, a, b, x){
    var U = D.unc, K = D.countries;
    if (a.n === b.n && a.c === b.c) return 0;
    var keepAll = a.c === b.c || (a.full && b.full), v = 0;
    if (a.c !== b.c) v += Math.pow(U.country[a.c], 2) + Math.pow(U.country[b.c], 2);
    [a, b].forEach(function(c){
      var h = 0.8 * weights(K[c.c], x)[3];
      v += Math.pow(h * U.rent[c.src], 2);
      if (c.full) v += Math.pow(U.own[c.c], 2) + (keepAll ? 0 : Math.pow(ownEffect(K, c, x), 2));
      else v += Math.pow(U.other, 2);
    });
    return Math.sqrt(v);
  }

  var api = {PTS: PTS, weights: weights, topPoint: topPoint, prices: prices, costRatio: costRatio, ownEffect: ownEffect, logError: logError};
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.RTSCore = api;
})(this);
