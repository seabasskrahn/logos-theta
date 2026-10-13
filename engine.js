/* Sonolumina engine (build 2026101301). Plain JS, pure functions, no network, no AI.
 * The approved equation:
 *   Sound(w,t) = F0 · R(w) · K(Ebar(v,t)) · [ Σ_u α_u · Sound(u,t) ] , resolved home (Res)
 *   F0 = 110 Hz (default only; tuning/Solfeggio/room/style are optional modifiers kept in index.html)
 *   s(w) = floor(12·frac(r(w)·φ)), r = first-appearance rank, φ = golden ratio
 *   J = [1,16/15,9/8,6/5,5/4,4/3,45/32,3/2,8/5,5/3,9/5,15/8]
 *   o(w) = 0 / 1 / 2 for count ≥200 / 20-199 / <20 (rarer = higher)
 *   T(w) = F0 · J[s] · 2^o ; companion snaps to a consonant ratio {1,3/2,4/3,5/4,6/5}
 *   E(v) = mean signed lexicon VAD (negation flips valence) ; Ebar = λ·E + (1-λ)·Ebar_prev
 *   K(E): mode from V (Aeolian < Dorian < Mixolydian < Ionian < Lydian), tempo 54-84 BPM from A,
 *         gain/register from D, notes snap to the mode
 *   cross-refs: Σ α_u·Sound(u), α normalised; crossfade x(t) (mine fades out while theirs fades in)
 *   Res: V-I at verse end, IV-I at chapter end, tonic last
 *   one clock: getState(t) -> {S, Ebar, t} for the visuals
 */
(function(root){'use strict';
const F0=110,PHI=(1+Math.sqrt(5))/2;
const J=[1,16/15,9/8,6/5,5/4,4/3,45/32,3/2,8/5,5/3,9/5,15/8];
const JS=['1/1','16/15','9/8','6/5','5/4','4/3','45/32','3/2','8/5','5/3','9/5','15/8'];
const CONS=[1,3/2,4/3,5/4,6/5];               // approved companion set
const CB_CONS=[1,5/4,4/3,3/2,2];               // index table used by the stored codebook/*.json files (decode only)
const frac=x=>x-Math.floor(x);
const step=r=>Math.floor(12*frac(r*PHI));
const octave=n=>n>=200?0:n>=20?1:2;
const fold=r=>{let o=1;while(r>=2){r/=2;o*=2}while(r<1){r*=2;o/=2}return[r,o]};
const nearest=(r,set)=>{let b=set[0];for(const c of set)if(Math.abs(Math.log(r/c))<Math.abs(Math.log(r/b)))b=c;return b};
const consSnapTo=(r,set)=>{const[x,o]=fold(r);return nearest(x,set)*o};
const consSnap=r=>consSnapTo(r,CB_CONS);       // legacy (verse drone), unchanged sound
const companion=r=>consSnapTo(r,CONS);         // approved companion snap
const tone=(s,o,f0)=>(f0||F0)*J[s]*Math.pow(2,o);
// stored codebook entry [step,octave,c1,c2,...] -> base tone + two companion partials
const entryHz=(x,f0)=>{const f=tone(x[0],x[1],f0);return[f,f*CB_CONS[x[2]],f*CB_CONS[x[3]]]};
// ---- E(v): signed lexicon VAD with negation flip; chapter smoothing
const NEG=/^(not|no|never|nor|neither|none|without|cannot)$/i;
function verseVAD(words,lex,win){win=win||3;let n=0,v=0,a=0,d=0;words.forEach((w,i)=>{const e=lex[String(w).toLowerCase()];if(!e)return;
 const neg=words.slice(Math.max(0,i-win),i).some(x=>NEG.test(x));v+=neg?1-e[0]:e[0];a+=e[1];d+=e[2];n++});
 return n?{v:v/n,a:a/n,d:d/n}:{v:.5,a:.5,d:.5}}
const smooth=(E,prev,l)=>{if(!prev)return Object.assign({},E);l=l==null?.5:l;return{v:l*E.v+(1-l)*prev.v,a:l*E.a+(1-l)*prev.a,d:l*E.d+(1-l)*prev.d}};
// ---- K(E)
const MODES={Lydian:[1,9/8,5/4,45/32,3/2,5/3,15/8],Ionian:[1,9/8,5/4,4/3,3/2,5/3,15/8],Mixolydian:[1,9/8,5/4,4/3,3/2,5/3,16/9],Dorian:[1,9/8,6/5,4/3,3/2,5/3,16/9],Aeolian:[1,9/8,6/5,4/3,3/2,8/5,9/5]};
const K=E=>{const v=E.v,a=E.a,d=E.d,mode=v>.7?(d>.6?'Lydian':'Ionian'):v>.5?'Mixolydian':v>.32?'Dorian':'Aeolian';
 return{mode,bpm:54+30*a,dens:a>.55?8:a>.3?6:4,loud:.75+.5*a,reg:Math.pow(2,(d-.5)*.6),bright:700+900*d,celV:.12+.08*d,strV:.04+.03*(1-a)+.02*d}};
const snapMode=(f,base,mode)=>{const[r,o]=fold(f/base);return base*nearest(r,MODES[mode].concat([2]))*o};
// Sound(w,t): word tone in the mode + companions (α 2/3, 1/3). mod = optional outside modifier (e.g. Solfeggio), default identity
function sound(hz,E,home,mod){mod=mod||(f=>f);const k=K(E||{v:.5,a:.5,d:.5}),f=mod(snapMode(hz[0],home,k.mode));
 return{f,mode:k.mode,parts:[[hz[1],2/3],[hz[2],1/3]].filter(p=>p[0]&&p[0]!=hz[0]).map(([h,al])=>({f:mod(snapMode(f*h/hz[0],home,k.mode)),a:al}))}}
// ---- harmony and Res
const DEG={I:[0,2,4],vi:[5,7,9],IV:[3,5,7],V:[4,6,8]},RING=['I','vi','IV','V'];
const deg=(sc,d)=>sc[d%7]*Math.pow(2,Math.floor(d/7));
const chordR=(mode,c,cad)=>DEG[c].map(d=>(cad&&c=='V'&&d%7==6)?15/8*Math.pow(2,Math.floor(d/7)):deg(MODES[mode],d));
const reg=(f,lo)=>{while(f<lo)f*=2;while(f>=lo*2)f/=2;return f};
function bestChord(mode,rel){let c0='I',bs=1e9;RING.forEach(c=>{let sc=0;rel.forEach(r=>{sc+=Math.min(...chordR(mode,c).map(t=>Math.abs(Math.log2(reg(r,1)/reg(t,1)))))});if(sc<bs-1e-9){bs=sc;c0=c}});return c0}
function progression(nb,c0,chEnd){const i0=RING.indexOf(c0),p=[...Array(nb)].map((_,b)=>RING[(i0+b)%4]);p[nb-1]='I';p[nb-2]=chEnd?'IV':'V';if(nb>2&&p[nb-3]==p[nb-2])p[nb-3]=chEnd?'vi':'IV';return p}
function pivot(from,to){if(from==to)return null;const same=c=>{const a=chordR(from,c),b=chordR(to,c);return a.every((x,i)=>Math.abs(x-b[i])<1e-9)};return['IV','V','vi','I'].find(same)||null}
// ---- cross-reference sum and crossfade
const alphas=w=>{const s=w.reduce((a,b)=>a+b,0)||1;return w.map(x=>x/s)};
const crossSum=(fs,al)=>fs.reduce((s,f,i)=>s+(al[i]||0)*f,0);
const xfade=(t,len)=>Math.min(1,Math.max(0,t/(len||1)));   // x(t): theirs = x, mine = 1-x
// ---- one clock
let ST={S:null,Ebar:{v:.5,a:.5,d:.5},t0:0};
function setState(o){ST=Object.assign({},ST,o);return ST}
function getState(t){return{S:ST.S,Ebar:ST.Ebar,t:t==null?0:t-ST.t0}}
const api={F0,PHI,J,JS,CONS,CB_CONS,frac,step,octave,tone,entryHz,consSnap,companion,NEG,verseVAD,smooth,MODES,K,snapMode,sound,DEG,RING,deg,chordR,reg,bestChord,progression,pivot,alphas,crossSum,xfade,setState,getState};
root.SonoEngine=api;if(typeof module!='undefined'&&module.exports)module.exports=api;
})(typeof window!='undefined'?window:globalThis);
