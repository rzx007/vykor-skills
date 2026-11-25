// Photo-based simplified geometry. See evidence.json for limits.
function pose(t){return {body:.26*ease(t,.40,1),canopy:.24*ease(t,.30,.91),lantern:.24*ease(t,.20,.82),cap:.24*ease(t,.10,.73),finial:.28*ease(t,0,.64)};}
// Five true apertures: surface patches stop at the hole boundary; an inner wall
// and stone reveals join the outer surface. They are not painted black circles.
function piercedBody(n){
 const rawProfile=curveProfile([[.53,.305],[.59,.367],[.70,.428],[.83,.46],[.92,.454],[1.04,.415],[1.13,.357],[1.20,.30]],8),maxRadius=Math.max(...rawProfile.map(p=>p[1])),profile=rawProfile.map(([z,r])=>[z,r*.46/maxRadius]);
 const min=.53,max=1.20,zc=.86,holeWidth=.235,holeHeight=.102,thickness=.052,sector=2*PI/5;
 function p(theta,z,inner=false){const r=profileRadius(profile,z)-(inner?thickness:0);return [r*Math.cos(theta),r*Math.sin(theta),z];}
 function boundary(u){if(Math.abs(u)>=holeWidth)return [zc,zc];const x=u/holeWidth,round=Math.sqrt(Math.max(0,1-x*x));return [zc-holeHeight*round,zc+holeHeight*round+.028*Math.pow(1-Math.abs(x),7)];}
 for(let j=0;j<5;j++){
  const center=-PI/4+j*sector;
  const us=[-sector/2];for(let k=0;k<=36;k++)us.push(-holeWidth+2*holeWidth*k/36);us.push(sector/2);
  for(let k=1;k<us.length;k++){
   const u0=us[k-1],u1=us[k],a=center+u0,b=center+u1,[lo0,hi0]=boundary(u0),[lo1,hi1]=boundary(u1);
   for(const inner of [false,true])for(const upper of [false,true])for(let v=0;v<22;v++){
    const f=v/22,g=(v+1)/22;
    const z=(lo,hi,t)=>upper?hi+(max-hi)*t:min+(lo-min)*t;
    poly(n,[p(a,z(lo0,hi0,f),inner),p(b,z(lo1,hi1,f),inner),p(b,z(lo1,hi1,g),inner),p(a,z(lo0,hi0,g),inner)],inner?C.interior:shade(C.wall,(a+b)/2),false);
   }
   if(u0>=-holeWidth&&u1<=holeWidth){for(const side of [0,1]){const za=side?hi0:lo0,zb=side?hi1:lo1;poly(n,[p(a,za),p(b,zb),p(b,zb,true),p(a,za,true)],C.stone,false);line(n,p(a,za),p(b,zb),C.ink);line(n,p(a,za,true),p(b,zb,true),C.soft);}}
  }
  // The wide raised surround is visible in both close-ups. Its outline is
  // represented in stone relief; unreadable ornamental curls are not invented.
  const surround=[];for(let k=0;k<=36;k++){const u=-holeWidth+2*holeWidth*k/36;surround.push([u,boundary(u)[0]]);}for(let k=35;k>0;k--){const u=-holeWidth+2*holeWidth*k/36;surround.push([u,boundary(u)[1]]);}
  const surroundPoint=(v,t)=>{const u=v[0]*(1+.42*t),z=zc+(v[1]-zc)*(1+.46*t),a=center+u,r=profileRadius(profile,z)+.003+.008*Math.sin(PI*t);return [r*Math.cos(a),r*Math.sin(a),z];};
  for(let k=0;k<surround.length;k++){const v=surround[k],w=surround[(k+1)%surround.length];for(let s=0;s<3;s++)poly(n,[surroundPoint(v,s/3),surroundPoint(w,s/3),surroundPoint(w,(s+1)/3),surroundPoint(v,(s+1)/3)],shade(C.stone,center),false);for(const t of [0,1])line(n,surroundPoint(v,t),surroundPoint(w,t),C.ink);}
 }
 // Do not draw a silhouette across an actual aperture at any viewing angle.
  n.contours.push({profile,surface:(z,r,a)=>[r*Math.cos(a),r*Math.sin(a),z],
   opening:(a,z)=>{const u=((a+PI/4+sector/2)%sector+sector)%sector-sector/2;const [lo,hi]=boundary(u);return z>lo&&z<hi;}});
 // Open top and bottom rims make the cavity legible in the exploded state.
 for(const z of [min,max])for(let j=0;j<120;j++){const a=j*PI/60,b=(j+1)*PI/60;poly(n,[p(a,z),p(b,z),p(b,z,true),p(a,z,true)],C.stone,false);line(n,p(a,z),p(b,z));line(n,p(a,z,true),p(b,z,true),C.soft);}
}
function hexLantern(n){
 // Six open windows with short jambs and a softly lobed head visible in photos.
 const radius=.205,z0=1.455,z1=1.60,opening0=1.47,u0=.27,u1=.73;
 const head=u=>{const x=(u-.5)/.23;return 1.54+.035*Math.sqrt(Math.max(0,1-x*x))-.006*Math.exp(-x*x*30);};
 for(let side=0;side<6;side++){
  const a=side*PI/3+PI/12,b=a+PI/3,pa=[radius*Math.cos(a),radius*Math.sin(a)],pb=[radius*Math.cos(b),radius*Math.sin(b)];
  const face=(u,z,inside=false)=>{const k=inside?.75:1;return [(pa[0]+(pb[0]-pa[0])*u)*k,(pa[1]+(pb[1]-pa[1])*u)*k,z];};
  const plate=(ua,ub,za,zb,zc,zd)=>{for(const inner of [false,true])poly(n,[face(ua,za,inner),face(ub,zb,inner),face(ub,zc,inner),face(ua,zd,inner)],inner?C.interior:C.wall,false);};
  plate(0,u0,z0,z0,z1,z1);plate(u1,1,z0,z0,z1,z1);plate(u0,u1,z0,z0,opening0,opening0);
  const contour=[[u0,opening0],[u1,opening0]];for(let j=0;j<=24;j++){const u=u1-(u1-u0)*j/24;contour.push([u,head(u)]);if(j<24){const v=u1-(u1-u0)*(j+1)/24;plate(v,u,head(v),head(u),z1,z1);}}
  contour.forEach((v,i)=>{const w=contour[(i+1)%contour.length];poly(n,[face(...v),face(...w),face(...w,true),face(...v,true)],C.stone,false);line(n,face(...v),face(...w));line(n,face(...v,true),face(...w,true),C.soft);});
  // Cap each face at its top and bottom without filling the window opening.
  for(const z of [z0,z1])poly(n,[face(0,z),face(1,z),face(1,z,true),face(0,z,true)],C.wall,false);
  line(n,face(0,z0),face(0,z1));line(n,face(0,z1),face(1,z1));
 }
}
const root=node('fixed water-level footing',null);
// Broken water ripples, with no filled disc that could be mistaken for masonry.
for(const [rr,start,end] of [[.77,.12,1.08],[.77,2.35,3.55],[.86,-1.30,-.35],[.86,1.45,2.15],[.90,3.65,4.35],[.90,.20,.85]])for(let j=0;j<32;j++){const a=start+(end-start)*j/32,b=start+(end-start)*(j+1)/32;line(root,[rr*Math.cos(a),rr*Math.sin(a),-.008],[rr*Math.cos(b),rr*Math.sin(b),-.008],C.soft);}
const base=node('06 stone base',root);
// Thin water-level footing; upright drum, rounded shoulder and a narrow neck.
lathe(base,[[0,.64],[.015,.69],[.045,.70],[.063,.67],[.075,.48],[.095,.48],[.112,.47],[.275,.47],[.293,.46],[.31,.442],[.325,.433],[.355,.425],[.395,.385],[.417,.335],[.435,.315],[.452,.312],[.510,.312],[.53,.305]],C.wall,{rings:[1,3,5,6,7,9,10,13,14,15,16,17]});
// Actual shapes stay rigid; only the gaps at documented component interfaces move.
const body=node('05 five-aperture body',base,p=>tr(0,0,p.body));piercedBody(body);
const canopy=node('04 lower canopy',body,p=>tr(0,0,p.canopy));
// Max diameter .86 / .92 = .935: slightly narrower than the body, as in photos.
lathe(canopy,[[1.20,.30],[1.213,.34],[1.228,.425],[1.242,.43],[1.277,.43],[1.289,.411],[1.309,.36],[1.33,.29],[1.34,.25]],C.roof,{rings:[0,3,4,8]});
const lantern=node('03 six-sided lantern',canopy,p=>tr(0,0,p.lantern));
lathe(lantern,curveProfile([[1.34,.25],[1.355,.263],[1.38,.267],[1.42,.265],[1.445,.245],[1.455,.205]],4),C.wall,{rings:[0,20]});hexLantern(lantern);
const cap=node('02 upper canopy',lantern,p=>tr(0,0,p.cap));
lathe(cap,[[1.60,.205],[1.615,.26],[1.631,.35],[1.645,.36],[1.687,.36],[1.70,.30],[1.716,.22],[1.72,.146]],C.roof,{rings:[0,3,4,7]});
const finial=node('01 gourd finial',cap,p=>tr(0,0,p.finial));
// Silhouette proportions traced from the user's close-up photo: a broad round
// lower bulb, a smaller upper bulb, a distinct narrow waist and a long neck.
// The waist must remain pronounced; flattening it to remove projected overlap
// changes the photographed form. These local proportions are photo estimates.
const finialProfile=smoothProfile([[1.72,.146],[1.745,.169],[1.78,.193],[1.82,.206],[1.855,.208],[1.89,.193],[1.925,.156],[1.955,.123],[1.978,.140],[2.01,.153],[2.04,.154],[2.08,.137],[2.12,.105],[2.16,.072],[2.20,.049],[2.24,.040],[2.28,.038],[2.32,.038]],20);
// Keep the finial surface plain: silhouette and end rings only, no meridians.
lathe(finial,finialProfile,C.wall,{segments:160,rings:[0,finialProfile.length-1]});
// A finial tenon is documented, but its hidden dimensions are unavailable;
// no invented tenon geometry or decorative relief is presented as measured.
const parts=[{node:finial,z:2.06,r:.166,zh:'01  葫芦顶',text:'GOURD FINIAL'},{node:cap,z:1.67,r:.36,zh:'02  上宝盖',text:'UPPER CANOPY'},{node:lantern,z:1.53,r:.205,zh:'03  六角小亭',text:'SIX-SIDED LANTERN'},{node:canopy,z:1.26,r:.43,zh:'04  下宝盖',text:'LOWER CANOPY'},{node:body,z:.86,r:.46,zh:'05  五孔塔身',text:'FIVE-APERTURE BODY'},{node:base,z:.24,r:.47,zh:'06  石质塔基',text:'STONE BASE'}];


return {
  root, parts, pose, pivotXY:[0,0],
  guides:()=>[[body,.53],[canopy,1.20],[lantern,1.34],[cap,1.60],[finial,1.72]].map(([n,z])=>({
    from:point(n.parent.world,[0,0,z]),
    to:point(n.world,n===finial?[.146*Math.cos(yaw),.146*Math.sin(yaw),z]:[0,0,z])
  })),
  dimension:{from:[0,0,0],to:[0,0,2.32],offset:.93,zh:'高度 · 2.32 米',en:'HEIGHT / 2.32 m'},
  inspect:{base,body,canopy,lantern,cap,finial,finialProfile}
};
