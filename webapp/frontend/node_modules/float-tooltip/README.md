Floating Tooltip
==============

[![NPM package][npm-img]][npm-url]
[![Build Size][build-size-img]][build-size-url]
[![NPM Downloads][npm-downloads-img]][npm-downloads-url]

A floating tooltip JS component.

## Quick start

```js
import Tooltip from 'float-tooltip';
```
or using a *script* tag
```html
<script src="//cdn.jsdelivr.net/npm/float-tooltip"></script>
```
then
```js
const myTooltip = new Tooltip(<triggerDOMElement>)
  .content('<div>Hello World!</div>');
```

## API reference

### Initialisation

```js
new Tooltip(<containerDomElement>, { configOptions })
```

| Config options | Description | Default |
| --- | --- | :--: |
| <b>style</b>: <i>object</i> | A custom style object apply to the tooltip and override the default style. | - |


### Methods

| Method | Description | Default                                                                                                                                                                                                                                           |
| --- | --- |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>content</b>([<i>string | HTMLElement</i>]) | Specify the content of the tooltip. Supports plain text, HTML string content, an [HTML element](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement) or [React JSX](https://react.dev/learn/writing-markup-with-jsx). If a falsy value is supplied the tooltip will automatically hide. | `false` |
| <b>offsetX</b>([<i>number</i>]) | The amount of pixels to offset the tooltip horizontally from its center position relative to the pointer. If a `null` value is specified (default) the offset will be automatically calculated and gradually shifted so it remains horizontally inside the parent element. | - |
| <b>offsetY</b>([<i>number</i>]) | The amount of pixels to offset the tooltip vertically relative to the pointer. A negative value will shift the tooltip to be above the pointer. If a `null` value is specified (default) the tooltip will be flipped above when the pointer is near the bottom, so it remains vertically inside the parent element. | - |

## Giving Back

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L398E7PKP47E8&currency_code=USD&source=url) If this project has helped you and you'd like to contribute back, you can always [buy me a ☕](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L398E7PKP47E8&currency_code=USD&source=url)!

[npm-img]: https://img.shields.io/npm/v/float-tooltip
[npm-url]: https://npmjs.org/package/float-tooltip
[build-size-img]: https://img.shields.io/bundlephobia/minzip/float-tooltip
[build-size-url]: https://bundlephobia.com/result?p=float-tooltip
[npm-downloads-img]: https://img.shields.io/npm/dt/float-tooltip
[npm-downloads-url]: https://www.npmtrends.com/float-tooltip
