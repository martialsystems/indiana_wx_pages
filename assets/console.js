/* Copyright (c) 2026 Martial Systems LLC */
(function () {
  "use strict";

  var PANELS = ["home", "outlook", "ledger", "nwm", "catalog", "maps"];

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function panelId(hash) {
    var id = (hash || "").replace(/^#/, "");
    if (PANELS.indexOf(id) >= 0) {
      return id;
    }
    if (id === "official" || id === "normals") {
      return "outlook";
    }
    return "home";
  }

  function showPanel(id) {
    id = panelId(id);
    $all("[data-panel]").forEach(function (el) {
      el.classList.toggle("is-on", el.getAttribute("data-panel") === id);
    });
    $all("nav.rail [data-go]").forEach(function (btn) {
      var on = btn.getAttribute("data-go") === id;
      btn.classList.toggle("is-on", on);
      if (on) {
        btn.setAttribute("aria-current", "page");
      } else {
        btn.removeAttribute("aria-current");
      }
    });
    if (location.hash.replace(/^#/, "") !== id) {
      if (history.replaceState) {
        history.replaceState(null, "", "#" + id);
      } else {
        location.hash = id;
      }
    }
  }

  function showNwm(product) {
    var tables = $all(".nwm-table");
    if (!tables.length) {
      return;
    }
    var match = tables.filter(function (el) {
      return el.getAttribute("data-product") === product;
    })[0];
    if (!match) {
      match = tables[0];
      product = match.getAttribute("data-product");
    }
    tables.forEach(function (el) {
      el.classList.toggle("is-on", el === match);
    });
    $all("[data-nwm]").forEach(function (btn) {
      btn.classList.toggle("is-on", btn.getAttribute("data-nwm") === product);
    });
  }

  function showMap(treeId) {
    var cards = $all(".map-card");
    if (!cards.length) {
      return;
    }
    var match = cards.filter(function (el) {
      return el.getAttribute("data-tree") === treeId;
    })[0];
    if (!match) {
      match = cards[0];
      treeId = match.getAttribute("data-tree");
    }
    cards.forEach(function (el) {
      el.classList.toggle("is-on", el === match);
    });
    $all("[data-map]").forEach(function (btn) {
      btn.classList.toggle("is-on", btn.getAttribute("data-map") === treeId);
    });
    if (match && match.scrollIntoView) {
      match.scrollIntoView({ block: "nearest" });
    }
  }

  function filterCatalog() {
    var laneBtn = $(".lane-keys [data-lane].is-on");
    var lane = laneBtn ? laneBtn.getAttribute("data-lane") : "all";
    var qEl = $("#catalog-q");
    var q = qEl ? qEl.value.toLowerCase() : "";
    $all("#catalog tbody tr").forEach(function (row) {
      var rowLane = row.getAttribute("data-lane") || "";
      var text = row.textContent.toLowerCase();
      var laneOk = lane === "all" || rowLane === lane;
      var qOk = !q || text.indexOf(q) >= 0;
      row.hidden = !(laneOk && qOk);
    });
  }

  function hrefAnchor(from) {
    var el = from;
    if (!el) {
      return null;
    }
    if (el.nodeType === 3) {
      el = el.parentElement;
    }
    if (!el || !el.closest) {
      return null;
    }
    return el.closest("a[href]");
  }

  function openViewer(src, caption) {
    var dlg = $("#viewer");
    var img = $("#viewer-img");
    var cap = $("#viewer-cap");
    if (!dlg || !img) {
      return;
    }
    img.src = src;
    img.alt = caption || "";
    if (cap) {
      cap.textContent = caption || "";
    }
    if (dlg.showModal) {
      dlg.showModal();
    } else {
      dlg.setAttribute("open", "open");
    }
  }

  function closeViewer() {
    var dlg = $("#viewer");
    if (!dlg) {
      return;
    }
    if (dlg.close) {
      dlg.close();
    } else {
      dlg.removeAttribute("open");
    }
  }

  function onReady() {
    if (document.body.classList.contains("tree-page")) {
      document.addEventListener("click", function (ev) {
        if (hrefAnchor(ev.target) && !ev.target.closest("img.zoom")) {
          return;
        }
        var zoom = ev.target.closest("img.zoom");
        if (zoom) {
          ev.preventDefault();
          openViewer(zoom.getAttribute("src"), zoom.getAttribute("alt") || "");
          return;
        }
        if (ev.target.closest("[data-close-viewer]")) {
          ev.preventDefault();
          closeViewer();
        }
      });
      document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape") {
          closeViewer();
        }
      });
      return;
    }
    showPanel(panelId(location.hash));
    var firstNwm = $(".nwm-table");
    if (firstNwm) {
      showNwm(firstNwm.getAttribute("data-product"));
    }
    var firstMap = $(".map-card");
    if (firstMap) {
      showMap(firstMap.getAttribute("data-tree"));
    }

    document.addEventListener("click", function (ev) {
      // Catalog/ledger GitHub links (including <code class="slug"> inside <a>).
      if (hrefAnchor(ev.target)) {
        return;
      }
      var go = ev.target.closest("[data-go]");
      if (go) {
        ev.preventDefault();
        showPanel(go.getAttribute("data-go"));
        var lane = go.getAttribute("data-lane");
        if (lane) {
          $all(".lane-keys [data-lane]").forEach(function (b) {
            b.classList.toggle("is-on", b.getAttribute("data-lane") === lane);
          });
          filterCatalog();
        }
        return;
      }
      var nwm = ev.target.closest("[data-nwm]");
      if (nwm) {
        ev.preventDefault();
        showPanel("nwm");
        showNwm(nwm.getAttribute("data-nwm"));
        return;
      }
      var mapBtn = ev.target.closest("[data-map]");
      if (mapBtn) {
        ev.preventDefault();
        showPanel("maps");
        showMap(mapBtn.getAttribute("data-map"));
        return;
      }
      var lane = ev.target.closest(".lane-keys [data-lane]");
      if (lane) {
        ev.preventDefault();
        $all(".lane-keys [data-lane]").forEach(function (b) {
          b.classList.toggle("is-on", b === lane);
        });
        filterCatalog();
        return;
      }
      var cat = ev.target.closest("[data-open-map]");
      if (cat) {
        ev.preventDefault();
        showPanel("maps");
        showMap(cat.getAttribute("data-open-map"));
        return;
      }
      var zoom = ev.target.closest("img.zoom");
      if (zoom) {
        ev.preventDefault();
        openViewer(zoom.getAttribute("src"), zoom.getAttribute("alt") || "");
        return;
      }
      if (ev.target.closest("[data-close-viewer]")) {
        ev.preventDefault();
        closeViewer();
      }
    });

    var qEl = $("#catalog-q");
    if (qEl) {
      qEl.addEventListener("input", filterCatalog);
    }

    window.addEventListener("hashchange", function () {
      showPanel(panelId(location.hash));
    });

    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        closeViewer();
      }
    });
    bootMermaid();
  }

  function bootMermaid() {
    if (!$(".mermaid")) {
      return;
    }
    var s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js";
    s.onload = function () {
      if (!window.mermaid) {
        return;
      }
      window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        theme: "base",
        themeVariables: {
          primaryColor: "#e6d5b8",
          primaryTextColor: "#1a140e",
          primaryBorderColor: "#b08d4a",
          lineColor: "#5c5144",
          secondaryColor: "#f3e6cc",
          tertiaryColor: "#efe0c2",
        },
      });
      window.mermaid.run({ querySelector: ".mermaid" });
    };
    document.head.appendChild(s);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();
