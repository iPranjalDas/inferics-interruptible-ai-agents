window.addEventListener('load', () => {
  let animated = false;
  // Use MutationObserver to wait until React mounts #root and main header exists
  const observer = new MutationObserver((mutations, obs) => {
    const mainHeader = document.querySelector("main header h1");
    if (mainHeader && !animated && window.gsap) {
      animated = true;
      obs.disconnect();
      
      // 3D GSAP Aesthetic Configuration (TasteSkill / OriginKit inspired)
      gsap.set("#root", { perspective: 1200 });
      gsap.set("main", { transformStyle: "preserve-3d" });

      // 1. Navbar slide down
      gsap.from("nav", {
        yPercent: -100,
        opacity: 0,
        duration: 1.2,
        ease: "power4.out"
      });

      // 2. Main Header Texts (Staggered 3D flip up)
      gsap.from("main header > div > div:first-child > *", {
        y: 40,
        rotationX: -45,
        opacity: 0,
        duration: 1.2,
        stagger: 0.15,
        ease: "back.out(1.2)",
        delay: 0.2
      });

      // 3. Quick Metrics Box (OriginKit style 3D float in)
      gsap.from("main header .shadow-xl", {
        rotationX: 25,
        rotationY: -15,
        z: -100,
        scale: 0.9,
        opacity: 0,
        duration: 1.5,
        ease: "elastic.out(1, 0.6)",
        delay: 0.4
      });

      // 4. Product Domain Cards (3D staggered pop-in)
      gsap.from(".grid > div", {
        y: 60,
        rotationX: 30,
        z: -50,
        opacity: 0,
        duration: 1,
        stagger: 0.08,
        ease: "power3.out",
        delay: 0.5
      });
      
      // 5. Chat Sidebar slide in
      gsap.from("aside", {
        xPercent: window.innerWidth >= 1024 ? 100 : 0,
        yPercent: window.innerWidth < 1024 ? 50 : 0,
        opacity: 0,
        duration: 1.2,
        ease: "expo.out",
        delay: 0.3
      });
    }
  });
  
  observer.observe(document.getElementById('root'), {
    childList: true,
    subtree: true
  });
});
