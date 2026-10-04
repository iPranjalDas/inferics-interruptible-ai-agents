window.addEventListener('load', () => {
  let animated = false;
  const observer = new MutationObserver((mutations, obs) => {
    const mainHeader = document.querySelector("main header h1");
    if (mainHeader && !animated && window.gsap) {
      animated = true;
      obs.disconnect();
      
      // ORIGINKIT + TASTESKILL + 21st.dev 3D AESTHETIC
      // Set deep 3D perspective and glassmorphism styling
      gsap.set("#root", { perspective: 1500 });
      gsap.set("main", { transformStyle: "preserve-3d" });

      // Add TasteSkill-style glass borders to all major cards dynamically
      document.querySelectorAll('.shadow-xl, .shadow-2xl, .border').forEach(el => {
        el.style.backgroundColor = 'rgba(10, 10, 15, 0.4)';
        el.style.backdropFilter = 'blur(20px)';
        el.style.WebkitBackdropFilter = 'blur(20px)';
        el.style.border = '1px solid rgba(255, 255, 255, 0.08)';
        el.style.boxShadow = '0 30px 60px -15px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1)';
      });

      // 1. Extreme 3D Title Entry (TasteSkill style)
      gsap.from("main header > div > div:first-child > *", {
        y: 100,
        z: -300,
        rotationX: -60,
        opacity: 0,
        duration: 1.8,
        stagger: 0.15,
        ease: "power4.out",
        delay: 0.2
      });

      // 2. Quick Metrics Box (Hovering Hologram)
      gsap.from("main header .shadow-xl", {
        rotationX: 45,
        rotationY: -20,
        z: -200,
        scale: 0.8,
        opacity: 0,
        duration: 2,
        ease: "elastic.out(1, 0.5)",
        delay: 0.5
      });

      // 3. Floating animation for the Metrics Box
      gsap.to("main header .shadow-xl", {
        y: 10,
        rotationX: 5,
        rotationY: -5,
        duration: 4,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 2.5
      });

      // 4. Product Domain Cards (3D cascade out of the screen)
      gsap.from(".grid > div", {
        y: 150,
        z: -100,
        rotationX: 45,
        opacity: 0,
        duration: 1.2,
        stagger: 0.1,
        ease: "expo.out",
        delay: 0.8
      });
      
      // 5. Chat Sidebar (Glass pane sliding in with 3D tilt)
      gsap.from("aside", {
        xPercent: 120,
        rotationY: -30,
        z: -200,
        opacity: 0,
        duration: 1.5,
        ease: "power3.out",
        delay: 0.6
      });
      
      // 6. Header
      gsap.from("nav", {
        yPercent: -150,
        opacity: 0,
        duration: 1.5,
        ease: "power4.out"
      });
    }
  });
  
  observer.observe(document.getElementById('root'), {
    childList: true,
    subtree: true
  });
});
