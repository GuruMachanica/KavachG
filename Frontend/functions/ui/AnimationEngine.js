// AnimationEngine.js - Anime.js Integration for Micro-Animations
export class AnimationEngine {
  staggerCards(selector = ".stat-card") {
    if (typeof anime === "undefined") return;
    anime({
      targets: selector,
      opacity: [0, 1],
      translateY: [24, 0],
      delay: anime.stagger(80),
      easing: "easeOutCubic",
      duration: 600,
    });
  }

  fadeIn(element, duration = 400) {
    if (typeof anime === "undefined" || !element) return;
    anime({
      targets: element,
      opacity: [0, 1],
      translateY: [12, 0],
      easing: "easeOutQuad",
      duration,
    });
  }

  countUp(element, endVal, duration = 800) {
    if (typeof anime === "undefined" || !element) {
      if (element) element.textContent = endVal;
      return;
    }
    const obj = { val: 0 };
    anime({
      targets: obj,
      val: endVal,
      round: 1,
      easing: "easeOutExpo",
      duration,
      update: () => {
        element.textContent = obj.val;
      },
    });
  }

  pulseAlert(element) {
    if (typeof anime === "undefined" || !element) return;
    anime({
      targets: element,
      scale: [1, 1.05, 1],
      easing: "easeInOutSine",
      duration: 400,
    });
  }
}

export const animationEngine = new AnimationEngine();
