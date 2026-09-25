# Vendored three.js

`three.module.min.js` and `OrbitControls.js` are copied here from the
official `three` npm package (v0.160.0, MIT license, see `LICENSE`), not
loaded from a CDN. `GLTFLoader.js` isn't vendored yet - it's only needed
once a real mesh exists to load (see `web/templates/simulation.html`'s
swap-in comment); add it the same way when that happens.

This is deliberate, not a workaround: the console is meant to run on a
Raspberry Pi on a local network, quite possibly with no general internet
access. A `/simulation` page that depends on `cdn.jsdelivr.net` (or any
CDN) at runtime would just be broken on that kind of deployment. Vendoring
a small, MIT-licensed, general-purpose library is the right call
regardless of what network the console happens to have.

To update: `npm install three@<version>` somewhere, then copy
`build/three.module.min.js` and `examples/jsm/controls/OrbitControls.js`
over these files (add `examples/jsm/loaders/GLTFLoader.js` too, once it's
actually needed).
