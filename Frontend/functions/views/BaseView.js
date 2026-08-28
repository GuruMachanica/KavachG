// BaseView.js - Abstract Base View Class
export class BaseView {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  render() {
    throw new Error("render() must be implemented by subclass");
  }

  escape(val) {
    return String(val ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
}
