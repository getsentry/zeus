import xhrmock from 'xhr-mock';

// This is so we can use async/await in tests instead of wrapping with `setTimeout`
window.tick = () => new Promise(resolve => setTimeout(resolve));

xhrmock.error(error => {
  console.error(error.err, {url: error.req.url()});
});
