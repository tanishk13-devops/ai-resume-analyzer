// Polyfill DOM objects for Vercel/serverless environments where pdfjs-dist requires them
if (typeof global.DOMMatrix === 'undefined') {
  global.DOMMatrix = class DOMMatrix {
    constructor() {}
  };
}

if (typeof global.ImageData === 'undefined') {
  global.ImageData = class ImageData {
    constructor() {}
  };
}

if (typeof global.Path2D === 'undefined') {
  global.Path2D = class Path2D {
    constructor() {}
  };
}
