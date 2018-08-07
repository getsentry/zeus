import React, { Component } from 'react';
import pixelMatch from 'pixelmatch';
import image1 from '../assets/screenshots/spot-1.jpg';
import image2 from '../assets/screenshots/spot-2.jpg';

export default class ImageDiff extends Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      firstImageLoaded: false,
      secondImageLoaded: false
    }
  }

  getImageData(image) {
    let canvas = this.refs.canvas;
    const width = image.clientWidth;
    const height = image.clientHeight;
    canvas.width = width;
    canvas.height = height;
    let context = canvas.getContext('2d');
    context.drawImage(image, 0, 0);
    return context.getImageData(0, 0, width, height);
  }

  diffImages() {
    let canvas = this.refs.canvas;
    let context = canvas.getContext('2d');

    const {image1, image2} = this.refs;

    const imgData1 = this.getImageData(image1);
    const imgData2 = this.getImageData(image2);

    const width = Math.max(image1.clientWidth, image1.clientWidth);
    const height = Math.max(image2.clientHeight, image2.clientHeight);

    debugger

    const diff = context.createImageData(width, height);

    pixelMatch(imgData1.data, imgData2.data, diff.data, width, height, {threshold: 0.1});

    context.putImageData(diff, 0, 0);
  }

  componentDidUpdate() {
    if (this.state.firstImageLoaded && this.state.secondImageLoaded) this.diffImages()
  }

  render() {
    return (
      <div>
        <img src={image1} crossOrigin="anonymous" ref="image1" onLoad={() => this.setState({firstImageLoaded: true})} />
        <img src={image2} crossOrigin="anonymous" ref="image2" onLoad={() => this.setState({secondImageLoaded: true})} />
        <canvas ref="canvas"></canvas>
      </div>
    );
  }
}
