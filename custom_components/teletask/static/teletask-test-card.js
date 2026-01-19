function t(t,e,s,i){var o,r=arguments.length,n=r<3?e:null===i?i=Object.getOwnPropertyDescriptor(e,s):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(t,e,s,i);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(n=(r<3?o(n):r>3?o(e,s,n):o(e,s))||n);return r>3&&n&&Object.defineProperty(e,s,n),n}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,s=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),o=new WeakMap;let r=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(s&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&o.set(e,t))}return t}toString(){return this.cssText}};const n=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:a,defineProperty:c,getOwnPropertyDescriptor:l,getOwnPropertyNames:d,getOwnPropertySymbols:h,getPrototypeOf:p}=Object,u=globalThis,_=u.trustedTypes,v=_?_.emptyScript:"",g=u.reactiveElementPolyfillSupport,b=(t,e)=>t,y={toAttribute(t,e){switch(e){case Boolean:t=t?v:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},m=(t,e)=>!a(t,e),f={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:m};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=f){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),i=this.getPropertyDescriptor(t,s,e);void 0!==i&&c(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){const{get:i,set:o}=l(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:i,set(e){const r=i?.call(this);o?.call(this,e),this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??f}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const t=p(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const t=this.properties,e=[...d(t),...h(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,i)=>{if(s)t.adoptedStyleSheets=i.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const s of i){const i=document.createElement("style"),o=e.litNonce;void 0!==o&&i.setAttribute("nonce",o),i.textContent=s.cssText,t.appendChild(i)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(void 0!==i&&!0===s.reflect){const o=(void 0!==s.converter?.toAttribute?s.converter:y).toAttribute(e,s.type);this._$Em=t,null==o?this.removeAttribute(i):this.setAttribute(i,o),this._$Em=null}}_$AK(t,e){const s=this.constructor,i=s._$Eh.get(t);if(void 0!==i&&this._$Em!==i){const t=s.getPropertyOptions(i),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:y;this._$Em=i;const r=o.fromAttribute(e,t.type);this[i]=r??this._$Ej?.get(i)??r,this._$Em=null}}requestUpdate(t,e,s,i=!1,o){if(void 0!==t){const r=this.constructor;if(!1===i&&(o=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??m)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:o},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==o||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===i&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,i=this[e];!0!==t||this._$AL.has(e)||void 0===i||this.C(e,void 0,s,i)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[b("elementProperties")]=new Map,$[b("finalized")]=new Map,g?.({ReactiveElement:$}),(u.reactiveElementVersions??=[]).push("2.1.2");const A=globalThis,x=t=>t,T=A.trustedTypes,S=T?T.createPolicy("lit-html",{createHTML:t=>t}):void 0,E="$lit$",w=`lit$${Math.random().toFixed(9).slice(2)}$`,C="?"+w,k=`<${C}>`,O=document,D=()=>O.createComment(""),P=t=>null===t||"object"!=typeof t&&"function"!=typeof t,U=Array.isArray,M="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,L=/>/g,H=RegExp(`>|${M}(?:([^\\s"'>=/]+)(${M}*=${M}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),j=/'/g,B=/"/g,z=/^(?:script|style|textarea|title)$/i,F=(t=>(e,...s)=>({_$litType$:t,strings:e,values:s}))(1),I=Symbol.for("lit-noChange"),G=Symbol.for("lit-nothing"),V=new WeakMap,q=O.createTreeWalker(O,129);function W(t,e){if(!U(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==S?S.createHTML(e):e}const K=(t,e)=>{const s=t.length-1,i=[];let o,r=2===e?"<svg>":3===e?"<math>":"",n=N;for(let e=0;e<s;e++){const s=t[e];let a,c,l=-1,d=0;for(;d<s.length&&(n.lastIndex=d,c=n.exec(s),null!==c);)d=n.lastIndex,n===N?"!--"===c[1]?n=R:void 0!==c[1]?n=L:void 0!==c[2]?(z.test(c[2])&&(o=RegExp("</"+c[2],"g")),n=H):void 0!==c[3]&&(n=H):n===H?">"===c[0]?(n=o??N,l=-1):void 0===c[1]?l=-2:(l=n.lastIndex-c[2].length,a=c[1],n=void 0===c[3]?H:'"'===c[3]?B:j):n===B||n===j?n=H:n===R||n===L?n=N:(n=H,o=void 0);const h=n===H&&t[e+1].startsWith("/>")?" ":"";r+=n===N?s+k:l>=0?(i.push(a),s.slice(0,l)+E+s.slice(l)+w+h):s+w+(-2===l?e:h)}return[W(t,r+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),i]};class Y{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[c,l]=K(t,e);if(this.el=Y.createElement(c,s),q.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(i=q.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes())for(const t of i.getAttributeNames())if(t.endsWith(E)){const e=l[r++],s=i.getAttribute(t).split(w),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:o,name:n[2],strings:s,ctor:"."===n[1]?tt:"?"===n[1]?et:"@"===n[1]?st:X}),i.removeAttribute(t)}else t.startsWith(w)&&(a.push({type:6,index:o}),i.removeAttribute(t));if(z.test(i.tagName)){const t=i.textContent.split(w),e=t.length-1;if(e>0){i.textContent=T?T.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],D()),q.nextNode(),a.push({type:2,index:++o});i.append(t[e],D())}}}else if(8===i.nodeType)if(i.data===C)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=i.data.indexOf(w,t+1));)a.push({type:7,index:o}),t+=w.length-1}o++}}static createElement(t,e){const s=O.createElement("template");return s.innerHTML=t,s}}function Z(t,e,s=t,i){if(e===I)return e;let o=void 0!==i?s._$Co?.[i]:s._$Cl;const r=P(e)?void 0:e._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(t),o._$AT(t,s,i)),void 0!==i?(s._$Co??=[])[i]=o:s._$Cl=o),void 0!==o&&(e=Z(t,o._$AS(t,e.values),o,i)),e}class J{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??O).importNode(e,!0);q.currentNode=i;let o=q.nextNode(),r=0,n=0,a=s[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new Q(o,o.nextSibling,this,t):1===a.type?e=new a.ctor(o,a.name,a.strings,this,t):6===a.type&&(e=new it(o,this,t)),this._$AV.push(e),a=s[++n]}r!==a?.index&&(o=q.nextNode(),r++)}return q.currentNode=O,i}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class Q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=G,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Z(this,t,e),P(t)?t===G||null==t||""===t?(this._$AH!==G&&this._$AR(),this._$AH=G):t!==this._$AH&&t!==I&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>U(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==G&&P(this._$AH)?this._$AA.nextSibling.data=t:this.T(O.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,i="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=Y.createElement(W(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{const t=new J(i,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=V.get(t.strings);return void 0===e&&V.set(t.strings,e=new Y(t)),e}k(t){U(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const o of t)i===e.length?e.push(s=new Q(this.O(D()),this.O(D()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=x(t).nextSibling;x(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,o){this.type=1,this._$AH=G,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=G}_$AI(t,e=this,s,i){const o=this.strings;let r=!1;if(void 0===o)t=Z(this,t,e,0),r=!P(t)||t!==this._$AH&&t!==I,r&&(this._$AH=t);else{const i=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=Z(this,i[s+n],e,n),a===I&&(a=this._$AH[n]),r||=!P(a)||a!==this._$AH[n],a===G?t=G:t!==G&&(t+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!i&&this.j(t)}j(t){t===G?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends X{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===G?void 0:t}}class et extends X{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==G)}}class st extends X{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){if((t=Z(this,t,e,0)??G)===I)return;const s=this._$AH,i=t===G&&s!==G||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==G&&(s===G||i);i&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class it{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){Z(this,t)}}const ot=A.litHtmlPolyfillSupport;ot?.(Y,Q),(A.litHtmlVersions??=[]).push("3.3.2");const rt=globalThis;class nt extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const i=s?.renderBefore??e;let o=i._$litPart$;if(void 0===o){const t=s?.renderBefore??null;i._$litPart$=o=new Q(e.insertBefore(D(),t),t,void 0,s??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return I}}nt._$litElement$=!0,nt.finalized=!0,rt.litElementHydrateSupport?.({LitElement:nt});const at=rt.litElementPolyfillSupport;at?.({LitElement:nt}),(rt.litElementVersions??=[]).push("4.2.2");const ct=t=>(e,s)=>{void 0!==s?s.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},lt={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:m},dt=(t=lt,e,s)=>{const{kind:i,metadata:o}=s;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===i&&((t=Object.create(t)).wrapped=!0),r.set(s.name,t),"accessor"===i){const{name:i}=s;return{set(s){const o=e.get.call(this);e.set.call(this,s),this.requestUpdate(i,o,t,!0,s)},init(e){return void 0!==e&&this.C(i,void 0,t,e),e}}}if("setter"===i){const{name:i}=s;return function(s){const o=this[i];e.call(this,s),this.requestUpdate(i,o,t,!0,s)}}throw Error("Unsupported decorator location: "+i)};function ht(t){return(e,s)=>"object"==typeof s?dt(t,e,s):((t,e,s)=>{const i=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),i?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}function pt(t){return ht({...t,state:!0,attribute:!1})}const ut=((t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1],t[0]);return new r(s,t,i)})`
  :host {
    display: block;
    --tt-primary-color: var(--primary-color, #03a9f4);
    --tt-accent-color: var(--accent-color, #ff9800);
    --tt-card-background: var(--card-background-color, #fff);
    --tt-primary-text: var(--primary-text-color, #212121);
    --tt-secondary-text: var(--secondary-text-color, #727272);
    --tt-divider-color: var(--divider-color, rgba(0, 0, 0, 0.12));
    --tt-border-radius: var(--ha-card-border-radius, 12px);
    --tt-spacing: 16px;
  }

  ha-card {
    padding: var(--tt-spacing);
    background: var(--tt-card-background);
    border-radius: var(--tt-border-radius);
  }

  /* Tab Bar */
  .tab-bar {
    display: flex;
    border-bottom: 2px solid var(--tt-divider-color);
    margin-bottom: var(--tt-spacing);
  }

  .tab {
    flex: 1;
    padding: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    color: var(--tt-secondary-text);
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
    user-select: none;
  }

  .tab:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .tab.active {
    color: var(--tt-primary-color);
    border-bottom-color: var(--tt-primary-color);
  }

  /* Form Elements */
  .form-group {
    margin-bottom: var(--tt-spacing);
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--tt-primary-text);
  }

  select,
  input[type="range"] {
    width: 100%;
    padding: 10px;
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: var(--tt-card-background);
    color: var(--tt-primary-text);
    font-size: 14px;
  }

  select:focus,
  input:focus {
    outline: none;
    border-color: var(--tt-primary-color);
  }

  /* Buttons */
  .button-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    background: var(--tt-primary-color);
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
  }

  button:hover {
    filter: brightness(110%);
    transform: translateY(-1px);
  }

  button:active {
    transform: translateY(0);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  button.secondary {
    background: var(--tt-secondary-text);
  }

  button.accent {
    background: var(--tt-accent-color);
  }

  button.danger {
    background: #f44336;
  }

  /* Control Panel */
  .control-panel {
    padding: var(--tt-spacing);
    border: 1px solid var(--tt-divider-color);
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.02);
  }

  /* Slider Container */
  .slider-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  input[type="range"] {
    flex: 1;
  }

  .slider-value {
    min-width: 50px;
    text-align: center;
    font-weight: 500;
    color: var(--tt-primary-text);
  }

  /* Result Box */
  .result-box {
    margin-top: var(--tt-spacing);
    padding: 12px;
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.02);
    min-height: 50px;
    color: var(--tt-primary-text);
  }

  .result-box.success {
    border-color: #4caf50;
    background: rgba(76, 175, 80, 0.1);
  }

  .result-box.error {
    border-color: #f44336;
    background: rgba(244, 67, 54, 0.1);
  }

  /* Event Log */
  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .log-controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .log-container {
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.02);
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .log-table {
    width: 100%;
    border-collapse: collapse;
  }

  .log-table th {
    position: sticky;
    top: 0;
    background: var(--tt-card-background);
    padding: 8px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--tt-divider-color);
    color: var(--tt-primary-text);
  }

  .log-table td {
    padding: 6px 8px;
    border-bottom: 1px solid var(--tt-divider-color);
    color: var(--tt-secondary-text);
  }

  .log-table tr:hover {
    background: rgba(0, 0, 0, 0.03);
  }

  .log-empty {
    padding: 20px;
    text-align: center;
    color: var(--tt-secondary-text);
  }

  /* Status Footer */
  .status-footer {
    margin-top: var(--tt-spacing);
    padding-top: var(--tt-spacing);
    border-top: 1px solid var(--tt-divider-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    color: var(--tt-secondary-text);
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #9e9e9e;
  }

  .status-dot.connected {
    background: #4caf50;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  /* Responsive */
  @media (max-width: 600px) {
    .button-group {
      flex-direction: column;
    }

    button {
      width: 100%;
    }

    .tab {
      padding: 10px 6px;
      font-size: 14px;
    }
  }

  /* Checkbox */
  .checkbox-container {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  input[type="checkbox"] {
    width: auto;
    cursor: pointer;
  }
`;let _t=class extends nt{constructor(){super(...arguments),this._selectedType="relay",this._dimmerValue=128,this._moodType="LOCAL",this._result="",this._resultType=""}_getDevicesByType(t){if(!this.hass)return[];const e=[],s=Object.values(this.hass.states);for(const i of s){if(!i.entity_id.includes("teletask"))continue;const s=i.attributes;if(!s)continue;let o=null,r=i.entity_id.split(".")[0];"relay"===t?"light"!==r&&"switch"!==r||1!==s.teletask_function||(o="relay"):"dimmer"===t?"light"===r&&2===s.teletask_function&&(o="dimmer"):"mood"===t?"button"===r&&[8,9,10].includes(s.teletask_function)&&(o="mood"):"flag"===t&&"binary_sensor"===r&&15===s.teletask_function&&(o="flag"),o&&e.push({entity_id:i.entity_id,number:s.teletask_number||0,room:s.room||"Unknown",name:s.friendly_name||i.entity_id,type:o,domain:r})}return e.sort((t,e)=>t.number-e.number)}_handleTypeChange(t){const e=t.target;this._selectedType=e.value,this._selectedDevice=void 0,this._result="",this._resultType=""}_handleDeviceChange(t){const e=t.target,s=this._getDevicesByType(this._selectedType);if(this._selectedDevice=s.find(t=>t.entity_id===e.value),this._result="",this._resultType="",this._selectedDevice&&"dimmer"===this._selectedType){const t=this.hass.states[this._selectedDevice.entity_id];t&&t.attributes.brightness&&(this._dimmerValue=t.attributes.brightness)}}async _handleRelayAction(t){if(this._selectedDevice)try{const e=this._selectedDevice.domain,s="toggle"===t?"toggle":`turn_${t}`;await this.hass.callService(e,s,{entity_id:this._selectedDevice.entity_id}),this._result=`${this._selectedDevice.name}: ${t.toUpperCase()} command sent`,this._resultType="success"}catch(t){this._result=`Error: ${t}`,this._resultType="error"}}async _handleDimmerSet(){if(this._selectedDevice)try{await this.hass.callService("light","turn_on",{entity_id:this._selectedDevice.entity_id,brightness:this._dimmerValue}),this._result=`${this._selectedDevice.name}: Set to ${this._dimmerValue}`,this._resultType="success"}catch(t){this._result=`Error: ${t}`,this._resultType="error"}}async _handleMoodAction(t){if(this._selectedDevice)try{const e="on"===t?"ON":"off"===t?"OFF":"TOGGLE";await this.hass.callService("teletask","set_mood",{number:this._selectedDevice.number,type:this._moodType,state:e}),this._result=`${this._selectedDevice.name} (${this._moodType}): ${t.toUpperCase()}`,this._resultType="success"}catch(t){this._result=`Error: ${t}`,this._resultType="error"}}_handleGetStatus(){if(this._selectedDevice)try{const t=this.hass.states[this._selectedDevice.entity_id];if(t){let e=`${this._selectedDevice.name}: ${t.state.toUpperCase()}`;"dimmer"===this._selectedType&&void 0!==t.attributes.brightness&&(e+=` (Brightness: ${t.attributes.brightness})`),this._result=e,this._resultType="success"}else this._result="Device state not available",this._resultType="error"}catch(t){this._result=`Error: ${t}`,this._resultType="error"}}_renderTypeSelector(){const t=this.config.show_device_types||["relay","dimmer","mood","flag"];return F`
      <div class="form-group">
        <label>Device Type:</label>
        <select @change=${this._handleTypeChange} .value=${this._selectedType}>
          ${t.map(t=>F`
              <option value=${t} ?selected=${t===this._selectedType}>
                ${t.charAt(0).toUpperCase()+t.slice(1)}
              </option>
            `)}
        </select>
      </div>
    `}_renderDeviceSelector(){const t=this._getDevicesByType(this._selectedType);return 0===t.length?F`
        <div class="form-group">
          <label>Select Device:</label>
          <div style="padding: 12px; color: var(--tt-secondary-text);">
            No ${this._selectedType}s configured in TeleTask integration.
          </div>
        </div>
      `:F`
      <div class="form-group">
        <label>Select Device:</label>
        <select @change=${this._handleDeviceChange}>
          <option value="" ?selected=${!this._selectedDevice}>Select a device...</option>
          ${t.map(t=>F`
              <option value=${t.entity_id} ?selected=${this._selectedDevice?.entity_id===t.entity_id}>
                [${t.number}] ${t.room} - ${t.name}
              </option>
            `)}
        </select>
      </div>
    `}_renderControlPanel(){return this._selectedDevice?"relay"===this._selectedType||"flag"===this._selectedType?F`
        <div class="control-panel">
          <div class="button-group">
            <button @click=${()=>this._handleRelayAction("on")}>ON</button>
            <button @click=${()=>this._handleRelayAction("off")} class="secondary">OFF</button>
            <button @click=${()=>this._handleRelayAction("toggle")} class="accent">TOGGLE</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `:"dimmer"===this._selectedType?F`
        <div class="control-panel">
          <div class="slider-container">
            <label style="margin: 0;">Brightness:</label>
            <input
              type="range"
              min="0"
              max="255"
              .value=${String(this._dimmerValue)}
              @input=${t=>{this._dimmerValue=parseInt(t.target.value)}}
            />
            <span class="slider-value">${this._dimmerValue}</span>
          </div>
          <div class="button-group">
            <button @click=${this._handleDimmerSet}>Set Dimmer</button>
            <button @click=${()=>this._handleRelayAction("toggle")} class="accent">Toggle</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `:"mood"===this._selectedType?F`
        <div class="control-panel">
          <div class="form-group">
            <label>Mood Type:</label>
            <select
              @change=${t=>{this._moodType=t.target.value}}
              .value=${this._moodType}
            >
              <option value="LOCAL">Local Mood</option>
              <option value="GENERAL">General Mood</option>
              <option value="TIMED">Timed Mood</option>
            </select>
          </div>
          <div class="button-group">
            <button @click=${()=>this._handleMoodAction("on")}>ON</button>
            <button @click=${()=>this._handleMoodAction("off")} class="secondary">OFF</button>
            <button @click=${()=>this._handleMoodAction("toggle")} class="accent">TOGGLE</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `:F`<div class="control-panel">Unsupported device type</div>`:F`<div class="control-panel">Select a device to control</div>`}_renderResult(){return this._result?F`<div class="result-box ${this._resultType}">${this._result}</div>`:F`<div class="result-box">Results will appear here...</div>`}render(){return F`
      <div class="device-control">
        ${this._renderTypeSelector()} ${this._renderDeviceSelector()} ${this._renderControlPanel()}

        <div style="margin-top: var(--tt-spacing);">
          <label>Last Result:</label>
          ${this._renderResult()}
        </div>
      </div>
    `}};_t.styles=ut,t([ht({attribute:!1})],_t.prototype,"hass",void 0),t([ht({attribute:!1})],_t.prototype,"config",void 0),t([pt()],_t.prototype,"_selectedType",void 0),t([pt()],_t.prototype,"_selectedDevice",void 0),t([pt()],_t.prototype,"_dimmerValue",void 0),t([pt()],_t.prototype,"_moodType",void 0),t([pt()],_t.prototype,"_result",void 0),t([pt()],_t.prototype,"_resultType",void 0),_t=t([ct("device-control-tab")],_t);const vt={1:"RELAY",2:"DIMMER",8:"LOCMOOD",9:"GENMOOD",10:"TIMEDMOOD",15:"FLAG",20:"SENSOR",21:"INPUT"};let gt=class extends nt{constructor(){super(...arguments),this._events=[],this._autoScroll=!0,this._isConnected=!1}connectedCallback(){super.connectedCallback(),this._subscribeToEvents(),this._checkConnection()}disconnectedCallback(){super.disconnectedCallback(),this._unsubscribe&&this._unsubscribe()}async _subscribeToEvents(){try{this._unsubscribe=await this.hass.connection.subscribeEvents(t=>this._handleEvent(t),"teletask_state_updated"),console.log("Subscribed to teletask_state_updated events")}catch(t){console.error("Failed to subscribe to TeleTask events:",t)}}_checkConnection(){if(this.hass&&this.hass.states){const t=Object.keys(this.hass.states).filter(t=>t.includes("teletask"));this._isConnected=t.length>0}}_handleEvent(t){const e={timestamp:(new Date).toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit",second:"2-digit"}),type:"EVENT",func:this._decodeFunctionName(t.data.func),num:t.data.num.toString(),state:this._formatState(t.data.state,t.data.func)};this._events=[...this._events,e];const s=this.config.max_events||100;this._events.length>s&&(this._events=this._events.slice(-s)),this._autoScroll&&this._scrollToBottom()}_decodeFunctionName(t){return vt[t]||`UNKNOWN(${t})`}_formatState(t,e){return 1===e||15===e?0===t?"OFF":255===t?"ON":`${t}`:2===e?`${t}`:8===e||9===e||10===e?0===t?"OFF":255===t?"ON":`${t}`:`${t}`}_scrollToBottom(){requestAnimationFrame(()=>{const t=this.shadowRoot?.querySelector(".log-container");t&&(t.scrollTop=t.scrollHeight)})}_handleClearLog(){this._events=[]}_handleAutoScrollToggle(t){this._autoScroll=t.target.checked}_renderLogHeader(){return F`
      <div class="log-header">
        <h3 style="margin: 0; color: var(--tt-primary-text);">TeleTask Communication Log</h3>
        <div class="log-controls">
          <div class="checkbox-container">
            <input
              type="checkbox"
              id="auto-scroll"
              ?checked=${this._autoScroll}
              @change=${this._handleAutoScrollToggle}
            />
            <label for="auto-scroll" style="margin: 0; cursor: pointer;">Auto-scroll</label>
          </div>
          <button @click=${this._handleClearLog} class="secondary">Clear Log</button>
        </div>
      </div>
    `}_renderLogTable(){return 0===this._events.length?F`
        <div class="log-container">
          <div class="log-empty">No events yet. Trigger a device to see communication logs.</div>
        </div>
      `:F`
      <div class="log-container">
        <table class="log-table">
          <thead>
            <tr>
              <th>TIME</th>
              <th>TYPE</th>
              <th>FUNC</th>
              <th>NUM</th>
              <th>STATE</th>
            </tr>
          </thead>
          <tbody>
            ${this._events.map(t=>F`
                <tr>
                  <td>${t.timestamp}</td>
                  <td>${t.type}</td>
                  <td>${t.func}</td>
                  <td>${t.num}</td>
                  <td>${t.state}</td>
                </tr>
              `)}
          </tbody>
        </table>
      </div>
    `}_renderStatusFooter(){return F`
      <div class="status-footer">
        <div>Events: ${this._events.length}</div>
        <div class="status-indicator">
          <span>Connection:</span>
          <div class="status-dot ${this._isConnected?"connected":""}"></div>
          <span>${this._isConnected?"Connected":"Disconnected"}</span>
        </div>
      </div>
    `}updated(t){t.has("hass")&&this._checkConnection()}render(){return F`
      <div class="event-monitor">
        ${this._renderLogHeader()} ${this._renderLogTable()} ${this._renderStatusFooter()}
      </div>
    `}};gt.styles=ut,t([ht({attribute:!1})],gt.prototype,"hass",void 0),t([ht({attribute:!1})],gt.prototype,"config",void 0),t([pt()],gt.prototype,"_events",void 0),t([pt()],gt.prototype,"_autoScroll",void 0),t([pt()],gt.prototype,"_isConnected",void 0),gt=t([ct("event-monitor-tab")],gt);let bt=class extends nt{constructor(){super(...arguments),this._activeTab="devices"}setConfig(t){if(!t)throw new Error("Invalid configuration");this._config={type:"custom:teletask-test-card",default_tab:t.default_tab||"devices",show_device_types:t.show_device_types||["relay","dimmer","mood","flag"],max_events:t.max_events||100,...t},this._activeTab=this._config.default_tab}static getConfigElement(){return document.createElement("teletask-test-card-editor")}static getStubConfig(){return{type:"custom:teletask-test-card",default_tab:"devices"}}getCardSize(){return 6}_handleTabClick(t){this._activeTab=t}render(){return this._config&&this.hass?F`
      <ha-card>
        <div class="tab-bar">
          <div
            class="tab ${"devices"===this._activeTab?"active":""}"
            @click=${()=>this._handleTabClick("devices")}
          >
            Devices
          </div>
          <div
            class="tab ${"events"===this._activeTab?"active":""}"
            @click=${()=>this._handleTabClick("events")}
          >
            Events
          </div>
        </div>

        <div class="tab-content">
          ${"devices"===this._activeTab?F`
                <device-control-tab
                  .hass=${this.hass}
                  .config=${this._config}
                ></device-control-tab>
              `:F`
                <event-monitor-tab
                  .hass=${this.hass}
                  .config=${this._config}
                ></event-monitor-tab>
              `}
        </div>
      </ha-card>
    `:F`
        <ha-card>
          <div style="padding: 16px;">
            Loading TeleTask Test Card...
          </div>
        </ha-card>
      `}};bt.styles=ut,t([ht({attribute:!1})],bt.prototype,"hass",void 0),t([pt()],bt.prototype,"_config",void 0),t([pt()],bt.prototype,"_activeTab",void 0),bt=t([ct("teletask-test-card")],bt),window.customCards=window.customCards||[],window.customCards.push({type:"teletask-test-card",name:"TeleTask Test Card",description:"Test TeleTask MICROS devices and monitor communication events in real-time.",preview:!1,documentationURL:"https://github.com/Zelenaar/hacs-teletask-micros-rs232"}),console.info("%c TELETASK-TEST-CARD %c v1.9.0 ","background-color: #03a9f4; color: #fff; font-weight: bold;","background-color: #333; color: #fff; font-weight: bold;");export{bt as TeletaskTestCard};
//# sourceMappingURL=teletask-test-card.js.map
