/* Gallery renderer.
 *
 * Everything is driven by gallery-data.js, which build_gallery.py writes.
 * Routes are hash based so the page also works when opened from disk:
 *
 *   #/                                  categories
 *   #/pycairo                           one category
 *   #/pycairo/render-engine             one group
 *   #/pycairo/render-engine?scene=fault line
 *                                       one group, filtered
 */

(function () {
    "use strict";

    var DATA = window.GALLERY_DATA || { categories: [], generated: null };

    var view = document.getElementById("view");
    var breadcrumb = document.getElementById("breadcrumb");
    var siteNav = document.getElementById("site-nav");
    var footerNote = document.getElementById("footer-note");

    var lightbox = document.getElementById("lightbox");
    var lightboxImage = document.getElementById("lightbox-image");
    var lightboxCaption = document.getElementById("lightbox-caption");

    // Items currently rendered, in display order. The lightbox walks these.
    var visibleItems = [];
    var lightboxIndex = -1;
    var lastFocused = null;

    /* ------------------------------------------------------------ helpers */

    function el(tag, props, children) {
        var node = document.createElement(tag);

        Object.keys(props || {}).forEach(function (key) {
            if (key === "class") {
                node.className = props[key];
            } else if (key === "text") {
                node.textContent = props[key];
            } else if (key.indexOf("on") === 0) {
                node.addEventListener(key.slice(2).toLowerCase(), props[key]);
            } else if (props[key] !== null && props[key] !== undefined) {
                node.setAttribute(key, props[key]);
            }
        });

        (children || []).forEach(function (child) {
            if (child) {
                node.appendChild(child);
            }
        });

        return node;
    }

    function clear(node) {
        while (node.firstChild) {
            node.removeChild(node.firstChild);
        }
    }

    function formatBytes(bytes) {
        if (!bytes) {
            return "";
        }

        var units = ["B", "KB", "MB", "GB"];
        var value = bytes;
        var unit = 0;

        while (value >= 1024 && unit < units.length - 1) {
            value /= 1024;
            unit += 1;
        }

        return (unit === 0 ? value : value.toFixed(1)) + " " + units[unit];
    }

    function plural(count, word) {
        return count + " " + word + (count === 1 ? "" : "s");
    }

    /* ------------------------------------------------------------ routing */

    function parseRoute() {
        var raw = window.location.hash.replace(/^#\/?/, "");
        var parts = raw.split("?");

        var segments = parts[0]
            .split("/")
            .filter(Boolean)
            .map(decodeURIComponent);

        return {
            segments: segments,
            params: new URLSearchParams(parts[1] || "")
        };
    }

    function buildHash(segments, params) {
        var path = segments.map(encodeURIComponent).join("/");
        var query = params ? params.toString() : "";

        return "#/" + path + (query ? "?" + query : "");
    }

    function findCategory(id) {
        return DATA.categories.filter(function (category) {
            return category.id === id;
        })[0];
    }

    function findGroup(category, id) {
        return category.groups.filter(function (group) {
            return group.id === id;
        })[0];
    }

    /* ------------------------------------------------------------ chrome */

    function renderBreadcrumb(trail) {
        clear(breadcrumb);

        trail.forEach(function (crumb, index) {
            if (index > 0) {
                breadcrumb.appendChild(el("span", { class: "sep", text: "/" }));
            }

            if (crumb.href) {
                breadcrumb.appendChild(
                    el("a", { href: crumb.href, text: crumb.label })
                );
            } else {
                breadcrumb.appendChild(
                    el("span", { class: "current", text: crumb.label })
                );
            }
        });
    }

    function renderNav(activeCategoryId) {
        clear(siteNav);

        DATA.categories.forEach(function (category) {
            siteNav.appendChild(
                el("a", {
                    href: buildHash([category.id]),
                    text: category.title,
                    class: category.id === activeCategoryId ? "active" : ""
                })
            );
        });
    }

    function renderFooter() {
        var total = DATA.categories.reduce(function (sum, category) {
            return sum + category.count;
        }, 0);

        var parts = [plural(total, "piece")];

        if (DATA.generated) {
            parts.push("built " + DATA.generated.replace("T", " "));
        }

        parts.push("rebuild with: python build_gallery.py");

        footerNote.textContent = parts.join("  ·  ");
    }

    /* ------------------------------------------------------------ tiles */

    function metaLine(item) {
        // The title already spells out the render engine fields, so only
        // show metadata that would otherwise be invisible.
        var bits = Object.keys(item.meta || {})
            .map(function (key) {
                return item.meta[key];
            })
            .filter(function (value) {
                return item.title.indexOf(value) === -1;
            });

        if (!bits.length && item.width) {
            bits.push(item.width + " × " + item.height);
        }

        return bits.join("  ·  ");
    }

    function createTile(item, index) {
        var image = el("img", {
            src: item.thumb,
            alt: item.title,
            loading: "lazy",
            decoding: "async"
        });

        if (item.width && item.height) {
            image.style.aspectRatio = item.width + " / " + item.height;
        }

        var meta = metaLine(item);

        return el(
            "button",
            {
                class: "tile",
                type: "button",
                onclick: function () {
                    openLightbox(index);
                }
            },
            [
                image,
                el("div", { class: "tile-body" }, [
                    el("div", { class: "tile-title", text: item.title }),
                    meta ? el("div", { class: "tile-meta", text: meta }) : null
                ])
            ]
        );
    }

    function createSketchCard(item) {
        var frame = el("div", { class: "sketch-frame" });

        var poster = el(
            "button",
            {
                class: "sketch-poster",
                type: "button",
                onclick: function () {
                    clear(frame);
                    frame.appendChild(
                        el("iframe", {
                            src: item.full,
                            title: item.title,
                            loading: "lazy"
                        })
                    );
                }
            },
            [
                el("span", { class: "play", text: "▶" }),
                el("span", { class: "hint", text: "run sketch" })
            ]
        );

        frame.appendChild(poster);

        return el("div", { class: "sketch-card" }, [
            frame,
            el("div", { class: "sketch-body" }, [
                el("h3", { text: item.title }),
                el("div", { class: "links" }, [
                    el("a", {
                        href: item.full,
                        target: "_blank",
                        rel: "noopener",
                        text: "open ↗"
                    })
                ])
            ])
        ]);
    }

    /* ------------------------------------------------------------ filters */

    function activeFilters(group, params) {
        var filters = {};

        (group.facets || []).forEach(function (facet) {
            var value = params.get(facet.key);

            if (value) {
                filters[facet.key] = value;
            }
        });

        return filters;
    }

    function applyFilters(items, filters) {
        var keys = Object.keys(filters);

        if (!keys.length) {
            return items;
        }

        return items.filter(function (item) {
            return keys.every(function (key) {
                return (item.meta || {})[key] === filters[key];
            });
        });
    }

    function createFacetControls(category, group, params) {
        if (!group.facets || !group.facets.length) {
            return null;
        }

        var rows = group.facets.map(function (facet) {
            var selected = params.get(facet.key);

            function chipFor(label, value) {
                var next = new URLSearchParams(params.toString());

                if (value === null || value === selected) {
                    next.delete(facet.key);
                } else {
                    next.set(facet.key, value);
                }

                var isActive =
                    value === null ? !selected : value === selected;

                return el("a", {
                    class: "chip" + (isActive ? " active" : ""),
                    href: buildHash([category.id, group.id], next),
                    text: label
                });
            }

            var chips = [chipFor("all", null)].concat(
                facet.values.map(function (value) {
                    return chipFor(value, value);
                })
            );

            return el("div", { class: "facet-row" }, [
                el("span", { class: "facet-label", text: facet.label })
            ].concat(chips));
        });

        return el("div", { class: "facets" }, rows);
    }

    /* ------------------------------------------------------------ pages */

    function renderHome() {
        renderBreadcrumb([{ label: "creative coding" }]);
        renderNav(null);
        visibleItems = [];

        var cards = DATA.categories.map(function (category) {
            var cover = category.cover
                ? el("img", {
                      class: "cover",
                      src: category.cover,
                      alt: "",
                      loading: "lazy"
                  })
                : el("div", { class: "cover-placeholder", text: "▶" });

            return el(
                "a",
                { class: "category-card", href: buildHash([category.id]) },
                [
                    cover,
                    el("div", { class: "body" }, [
                        el("h2", { text: category.title }),
                        el("p", { text: category.blurb }),
                        el("span", {
                            class: "count",
                            text: plural(category.count, "piece")
                        })
                    ])
                ]
            );
        });

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: "creative coding" }),
                el("p", {
                    text:
                        "generated drawings from this repository, grouped by " +
                        "the toolkit that made them."
                })
            ])
        );
        view.appendChild(el("div", { class: "category-grid" }, cards));
    }

    function renderGroupSection(category, group, params, withHeading) {
        var fragment = document.createDocumentFragment();

        if (withHeading) {
            fragment.appendChild(
                el("div", { class: "section-head" }, [
                    el("h2", { text: group.title }),
                    el("span", {
                        class: "count",
                        text: plural(group.items.length, "piece")
                    })
                ])
            );
        }

        if (group.blurb) {
            fragment.appendChild(
                el("p", { class: "section-blurb", text: group.blurb })
            );
        }

        var controls = createFacetControls(category, group, params);

        if (controls) {
            fragment.appendChild(controls);
        }

        var items = applyFilters(
            group.items,
            activeFilters(group, params)
        );

        if (!items.length) {
            fragment.appendChild(
                el("p", { class: "empty", text: "nothing matches this filter." })
            );
            return fragment;
        }

        if (group.kind === "sketch") {
            fragment.appendChild(
                el(
                    "div",
                    { class: "sketch-grid" },
                    items.map(createSketchCard)
                )
            );
            return fragment;
        }

        var offset = visibleItems.length;
        visibleItems = visibleItems.concat(items);

        fragment.appendChild(
            el(
                "div",
                { class: "tile-grid" },
                items.map(function (item, index) {
                    return createTile(item, offset + index);
                })
            )
        );

        return fragment;
    }

    function renderCategory(category, params) {
        renderBreadcrumb([
            { label: "creative coding", href: "#/" },
            { label: category.title }
        ]);
        renderNav(category.id);
        visibleItems = [];

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: category.title }),
                el("p", { text: category.blurb })
            ])
        );

        // A single group needs no extra hop: show its grid straight away.
        if (category.groups.length === 1) {
            view.appendChild(
                renderGroupSection(category, category.groups[0], params, false)
            );
            return;
        }

        var cards = category.groups.map(function (group) {
            var cover = group.items.filter(function (item) {
                return item.thumb;
            })[0];

            return el(
                "a",
                {
                    class: "category-card",
                    href: buildHash([category.id, group.id])
                },
                [
                    cover
                        ? el("img", {
                              class: "cover",
                              src: cover.thumb,
                              alt: "",
                              loading: "lazy"
                          })
                        : el("div", { class: "cover-placeholder", text: "▶" }),
                    el("div", { class: "body" }, [
                        el("h2", { text: group.title }),
                        el("p", { text: group.blurb }),
                        el("span", {
                            class: "count",
                            text: plural(group.items.length, "piece")
                        })
                    ])
                ]
            );
        });

        view.appendChild(el("div", { class: "category-grid" }, cards));
    }

    function renderGroup(category, group, params) {
        renderBreadcrumb([
            { label: "creative coding", href: "#/" },
            { label: category.title, href: buildHash([category.id]) },
            { label: group.title }
        ]);
        renderNav(category.id);
        visibleItems = [];

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: group.title }),
                el("p", { text: category.title + " · " + group.directory })
            ])
        );

        view.appendChild(renderGroupSection(category, group, params, false));
    }

    function render() {
        var route = parseRoute();
        var category = findCategory(route.segments[0]);

        closeLightbox();

        if (!category) {
            renderHome();
        } else if (route.segments.length === 1) {
            renderCategory(category, route.params);
        } else {
            var group = findGroup(category, route.segments[1]);

            if (group) {
                renderGroup(category, group, route.params);
            } else {
                renderCategory(category, route.params);
            }
        }

        window.scrollTo(0, 0);
    }

    /* ------------------------------------------------------------ lightbox */

    function openLightbox(index) {
        if (index < 0 || index >= visibleItems.length) {
            return;
        }

        lastFocused = document.activeElement;
        lightboxIndex = index;

        var item = visibleItems[index];

        lightboxImage.src = item.full;
        lightboxImage.alt = item.title;

        clear(lightboxCaption);
        lightboxCaption.appendChild(el("strong", { text: item.title }));

        Object.keys(item.meta || {}).forEach(function (key) {
            lightboxCaption.appendChild(
                el("span", { text: key + ": " + item.meta[key] })
            );
        });

        if (item.width) {
            lightboxCaption.appendChild(
                el("span", {
                    text:
                        item.width +
                        " × " +
                        item.height +
                        "  ·  " +
                        formatBytes(item.bytes)
                })
            );
        }

        lightboxCaption.appendChild(
            el("span", {}, [
                el("a", {
                    href: item.full,
                    target: "_blank",
                    rel: "noopener",
                    text: "full size ↗"
                })
            ])
        );

        if (item.source) {
            lightboxCaption.appendChild(
                el("span", {}, [
                    el("a", {
                        href: item.source,
                        target: "_blank",
                        rel: "noopener",
                        text: item.sourceLabel + " ↗"
                    })
                ])
            );
        }

        lightbox.hidden = false;
        document.body.style.overflow = "hidden";
        document.getElementById("lightbox-close").focus();
    }

    function closeLightbox() {
        if (lightbox.hidden) {
            return;
        }

        lightbox.hidden = true;
        lightboxImage.removeAttribute("src");
        document.body.style.overflow = "";

        if (lastFocused && lastFocused.focus) {
            lastFocused.focus();
        }
    }

    function stepLightbox(delta) {
        if (lightbox.hidden || !visibleItems.length) {
            return;
        }

        var next =
            (lightboxIndex + delta + visibleItems.length) % visibleItems.length;

        openLightbox(next);
    }

    document
        .getElementById("lightbox-close")
        .addEventListener("click", closeLightbox);

    document
        .getElementById("lightbox-prev")
        .addEventListener("click", function () {
            stepLightbox(-1);
        });

    document
        .getElementById("lightbox-next")
        .addEventListener("click", function () {
            stepLightbox(1);
        });

    lightbox.addEventListener("click", function (event) {
        if (event.target === lightbox || event.target.tagName === "FIGURE") {
            closeLightbox();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (lightbox.hidden) {
            return;
        }

        if (event.key === "Escape") {
            closeLightbox();
        } else if (event.key === "ArrowLeft") {
            stepLightbox(-1);
        } else if (event.key === "ArrowRight") {
            stepLightbox(1);
        }
    });

    /* ------------------------------------------------------------ start */

    window.addEventListener("hashchange", render);

    if (!DATA.categories.length) {
        clear(view);
        view.appendChild(
            el("p", {
                class: "empty",
                text:
                    "no gallery data found. run: python build_gallery.py"
            })
        );
    } else {
        renderFooter();
        render();
    }
})();
