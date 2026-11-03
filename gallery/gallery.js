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
 *   #/worlds                            every piece, from every toolkit
 *   #/worlds?world=cosmic&system=oscillators
 *                                       every piece, filtered
 *   #/worlds/cosmos_origin              one piece and its related pieces
 */

(function () {
    "use strict";

    var DATA = window.GALLERY_DATA || { categories: [], generated: null };

    var VOCABULARY = DATA.vocabulary || {
        worlds: [],
        systems: [],
        interactions: [],
        modes: []
    };

    // The worlds view and the piece pages live here. build_gallery.py
    // refuses a category with this id.
    var WORLDS_ROUTE = "worlds";

    // Facet keys that read item.taxonomy instead of item.meta. A world
    // filter matches a piece's primary world or any of its secondary ones.
    var TAXONOMY_FACETS = {
        world: function (taxonomy) {
            return [taxonomy.world].concat(taxonomy.worlds);
        },
        system: function (taxonomy) {
            return taxonomy.systems;
        },
        interaction: function (taxonomy) {
            return taxonomy.interactions;
        }
    };

    var RELATED_LIMIT = 6;

    // A tile shows at most a 2:1 window of its image, either way round.
    // Anything longer (jpger_76 and jpger_77 are 8:1 strips) is cropped
    // to that window instead of becoming a sliver or a tile thousands of
    // pixels tall. build_gallery.py sizes those thumbnails with the same
    // limit (TILE_MAX_ASPECT there), so the crop stays sharp.
    var TILE_MAX_ASPECT = 2;

    // Every piece with the category and group it belongs to, in data order.
    var PIECES = [];
    var PIECE_BY_ID = Object.create(null);

    DATA.categories.forEach(function (category) {
        category.groups.forEach(function (group) {
            group.items.forEach(function (item) {
                var piece = { item: item, category: category, group: group };

                PIECES.push(piece);
                PIECE_BY_ID[item.id] = piece;
            });
        });
    });

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

    // "noise-fields" reads as "noise fields".
    function slugLabel(slug) {
        return slug.replace(/-/g, " ");
    }

    function findById(list, id) {
        return list.filter(function (entry) {
            return entry.id === id;
        })[0];
    }

    // Puts a separator text node between nodes.
    function joined(nodes, separator) {
        return nodes.reduce(function (result, node, index) {
            if (index > 0) {
                result.push(document.createTextNode(separator));
            }

            result.push(node);
            return result;
        }, []);
    }

    // The taxonomy every item of a list shares, or null if they differ.
    // Image series share one today, but a series may override pieces later.
    function sharedTaxonomy(items) {
        var first = items.length ? items[0].taxonomy : null;

        if (!first) {
            return null;
        }

        var key = JSON.stringify(first);

        return items.every(function (item) {
            return JSON.stringify(item.taxonomy) === key;
        })
            ? first
            : null;
    }

    // "world:abstract", "system:noise-fields", ... for comparing pieces.
    function tagsOf(taxonomy) {
        if (!taxonomy) {
            return [];
        }

        return Object.keys(TAXONOMY_FACETS).reduce(function (tags, key) {
            return tags.concat(
                TAXONOMY_FACETS[key](taxonomy).map(function (value) {
                    return key + ":" + value;
                })
            );
        }, []);
    }

    function tagLabel(tag) {
        return slugLabel(tag.slice(tag.indexOf(":") + 1));
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

        if (VOCABULARY.worlds.length) {
            siteNav.appendChild(
                el("a", {
                    href: buildHash([WORLDS_ROUTE]),
                    text: "worlds",
                    class: activeCategoryId === WORLDS_ROUTE ? "active" : ""
                })
            );
            siteNav.appendChild(
                el("span", { class: "nav-sep", "aria-hidden": "true" })
            );
        }

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

    // Width over height for the tile, inside the 2:1 limit.
    function tileAspect(item) {
        if (!item.width || !item.height) {
            return 1;
        }

        return Math.min(
            TILE_MAX_ASPECT,
            Math.max(1 / TILE_MAX_ASPECT, item.width / item.height)
        );
    }

    function createTile(item, index) {
        var aspect = tileAspect(item);

        var image = el("img", {
            src: item.thumb,
            alt: item.title,
            loading: "lazy",
            decoding: "async"
        });

        image.style.aspectRatio = String(aspect);

        var meta = metaLine(item);

        var tile = el(
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

        // gallery.css sizes the tile from this, so every image in a row
        // gets the same height.
        tile.style.setProperty("--aspect", aspect.toFixed(4));

        return tile;
    }

    function createSketchFrame(item) {
        var frame = el("div", { class: "sketch-frame" });

        var poster = el(
            "button",
            {
                class: "sketch-poster",
                type: "button",
                onclick: function () {
                    var iframe = el("iframe", {
                        src: item.full,
                        title: item.title,
                        loading: "lazy"
                    });

                    clear(frame);
                    frame.appendChild(iframe);

                    // The poster is gone, so hand focus to the sketch
                    // rather than dropping it on the page.
                    iframe.focus();
                }
            },
            [
                el("span", { class: "play", text: "▶" }),
                el("span", { class: "hint", text: "run sketch" })
            ]
        );

        frame.appendChild(poster);

        return frame;
    }

    // In the worlds view a card also says what the sketch is and links to
    // its own page.
    function createSketchCard(item, withDetails) {
        var links = [
            el("a", {
                href: item.full,
                target: "_blank",
                rel: "noopener",
                text: "open ↗"
            })
        ];

        var details = null;

        if (withDetails) {
            links.unshift(el("a", { href: pieceHash(item), text: "about" }));

            if (item.taxonomy) {
                details = el("div", { class: "sketch-details" }, [
                    taxonomyLine(item.taxonomy),
                    item.taxonomy.concept
                        ? el("p", {
                              class: "concept",
                              text: item.taxonomy.concept
                          })
                        : null
                ]);
            }
        }

        return el("div", { class: "sketch-card" }, [
            createSketchFrame(item),
            el("div", { class: "sketch-body" }, [
                el("h3", { text: item.title }),
                el("div", { class: "links" }, links)
            ]),
            details
        ]);
    }

    /* ------------------------------------------------------------ taxonomy */

    function pieceHash(item) {
        return buildHash([WORLDS_ROUTE, item.id]);
    }

    function tagLink(key, value, className) {
        return el("a", {
            class: className || null,
            href: buildHash([WORLDS_ROUTE], new URLSearchParams([[key, value]])),
            text: slugLabel(value)
        });
    }

    // "abstract (fluid) · noise fields, procedural geometry", each part
    // linking to the worlds view filtered by it.
    function taxonomyLine(taxonomy) {
        var parts = [el("strong", {}, [tagLink("world", taxonomy.world)])];

        if (taxonomy.worlds.length) {
            parts.push(document.createTextNode(" ("));
            parts = parts.concat(
                joined(
                    taxonomy.worlds.map(function (world) {
                        return tagLink("world", world);
                    }),
                    ", "
                )
            );
            parts.push(document.createTextNode(")"));
        }

        [
            ["system", taxonomy.systems],
            ["interaction", taxonomy.interactions]
        ].forEach(function (pair) {
            if (!pair[1].length) {
                return;
            }

            parts.push(document.createTextNode("  ·  "));
            parts = parts.concat(
                joined(
                    pair[1].map(function (value) {
                        return tagLink(pair[0], value);
                    }),
                    ", "
                )
            );
        });

        return el("p", { class: "taxonomy-line" }, parts);
    }

    /* ------------------------------------------------------------ filters */

    // The values an item has for a facet key, as a list, so one filter
    // works for single values in meta and for lists in the taxonomy.
    function facetValues(item, key) {
        if (TAXONOMY_FACETS[key]) {
            return item.taxonomy ? TAXONOMY_FACETS[key](item.taxonomy) : [];
        }

        var value = (item.meta || {})[key];

        return value ? [value] : [];
    }

    function activeFilters(facets, params) {
        var filters = {};

        facets.forEach(function (facet) {
            var value = params.get(facet.key);

            if (value) {
                filters[facet.key] = value;
            }
        });

        return filters;
    }

    function matchesFilters(item, filters, ignoredKey) {
        return Object.keys(filters).every(function (key) {
            return (
                key === ignoredKey ||
                facetValues(item, key).indexOf(filters[key]) !== -1
            );
        });
    }

    function applyFilters(items, filters) {
        if (!Object.keys(filters).length) {
            return items;
        }

        return items.filter(function (item) {
            return matchesFilters(item, filters);
        });
    }

    // Chips link to the view at segments with one facet value changed. When
    // items are given, each chip also counts the pieces it would show, and a
    // value that would show none stays visible but can't be chosen.
    function createFacetControls(facets, params, segments, items) {
        if (!facets.length) {
            return null;
        }

        var filters = activeFilters(facets, params);

        var rows = facets.map(function (facet) {
            var selected = params.get(facet.key);

            // What the other active filters leave for this facet to split.
            var pool = items
                ? items.filter(function (item) {
                      return matchesFilters(item, filters, facet.key);
                  })
                : null;

            function chipFor(label, value) {
                var next = new URLSearchParams(params.toString());

                if (value === null || value === selected) {
                    next.delete(facet.key);
                } else {
                    next.set(facet.key, value);
                }

                var isActive =
                    value === null ? !selected : value === selected;

                var title =
                    value !== null && facet.titles
                        ? facet.titles[value] || null
                        : null;

                var count = null;

                if (pool) {
                    count =
                        value === null
                            ? pool.length
                            : pool.filter(function (item) {
                                  return (
                                      facetValues(item, facet.key).indexOf(
                                          value
                                      ) !== -1
                                  );
                              }).length;
                }

                var children = [document.createTextNode(label)];

                if (count !== null) {
                    children.push(
                        el("span", { class: "chip-count", text: count })
                    );
                }

                if (count === 0 && !isActive) {
                    return el(
                        "span",
                        {
                            class: "chip disabled",
                            "aria-disabled": "true",
                            title: (title ? title + ", " : "") + "nothing yet"
                        },
                        children
                    );
                }

                return el(
                    "a",
                    {
                        class: "chip" + (isActive ? " active" : ""),
                        href: buildHash(segments, next),
                        title: title,
                        "aria-current": isActive ? "true" : null,
                        // Lets render() give focus back after the reload.
                        "data-chip":
                            facet.key + "=" + (value === null ? "" : value)
                    },
                    children
                );
            }

            var chips = [chipFor("all", null)].concat(
                facet.values.map(function (value) {
                    return chipFor(
                        facet.format ? facet.format(value) : value,
                        value
                    );
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

        if (VOCABULARY.worlds.length) {
            cards.unshift(createWorldsCard());
        }

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: "creative coding" }),
                el("p", {
                    text:
                        "generated drawings and live sketches from this " +
                        "repository, by the world they belong to or the " +
                        "toolkit that made them."
                })
            ])
        );
        view.appendChild(el("div", { class: "category-grid" }, cards));
    }

    function worldHasPieces(world) {
        return PIECES.some(function (piece) {
            return facetValues(piece.item, "world").indexOf(world.id) !== -1;
        });
    }

    // Its cover names every world, with the empty ones dimmed.
    function createWorldsCard() {
        var populated = VOCABULARY.worlds.filter(worldHasPieces);

        return el(
            "a",
            { class: "category-card", href: buildHash([WORLDS_ROUTE]) },
            [
                el(
                    "div",
                    { class: "cover-worlds", "aria-hidden": "true" },
                    VOCABULARY.worlds.map(function (world) {
                        return el("span", {
                            class: populated.indexOf(world) === -1 ? "unpopulated" : "",
                            text: world.id
                        });
                    })
                ),
                el("div", { class: "body" }, [
                    el("h2", { text: "worlds" }),
                    el("p", {
                        text:
                            "every piece from every toolkit, by the world it " +
                            "belongs to: how it looks, the system that " +
                            "drives it and the idea it explores."
                    }),
                    el("span", {
                        class: "count",
                        text:
                            plural(PIECES.length, "piece") +
                            " in " +
                            plural(populated.length, "world")
                    })
                ])
            ]
        );
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

        var facets = group.facets || [];

        var controls = createFacetControls(facets, params, [
            category.id,
            group.id
        ]);

        if (controls) {
            fragment.appendChild(controls);
        }

        var items = applyFilters(group.items, activeFilters(facets, params));

        if (!items.length) {
            fragment.appendChild(
                el("p", { class: "empty", text: "nothing matches this filter." })
            );
            return fragment;
        }

        fragment.appendChild(createItemGrid(group, items, false));

        return fragment;
    }

    // Sketches get cards, images get tiles that the lightbox can walk.
    function createItemGrid(group, items, withDetails) {
        if (group.kind === "sketch") {
            return el(
                "div",
                { class: "sketch-grid" },
                items.map(function (item) {
                    return createSketchCard(item, withDetails);
                })
            );
        }

        var offset = visibleItems.length;
        visibleItems = visibleItems.concat(items);

        return el(
            "div",
            { class: "tile-grid" },
            items.map(function (item, index) {
                return createTile(item, offset + index);
            })
        );
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

    /* ------------------------------------------------------------ worlds */

    // The world row lists all twelve worlds, empty ones included, so the
    // view shows the whole map. Systems and interactions list only what
    // some piece uses.
    function buildWorldFacets() {
        function ids(list) {
            return list.map(function (entry) {
                return entry.id;
            });
        }

        function titles(list, field) {
            var map = {};

            list.forEach(function (entry) {
                map[entry.id] = entry[field];
            });

            return map;
        }

        function used(key) {
            return function (value) {
                return PIECES.some(function (piece) {
                    return facetValues(piece.item, key).indexOf(value) !== -1;
                });
            };
        }

        return [
            {
                key: "world",
                label: "World",
                values: ids(VOCABULARY.worlds),
                titles: titles(VOCABULARY.worlds, "identity"),
                format: slugLabel
            },
            {
                key: "system",
                label: "System",
                values: ids(VOCABULARY.systems).filter(used("system")),
                titles: titles(VOCABULARY.systems, "label"),
                format: slugLabel
            },
            {
                key: "interaction",
                label: "Interaction",
                values: ids(VOCABULARY.interactions).filter(used("interaction")),
                titles: titles(VOCABULARY.interactions, "label"),
                format: slugLabel
            }
        ];
    }

    var WORLD_FACETS = buildWorldFacets();

    // Live sketches first, then the image series, each in data order.
    function worldSections(filters) {
        var live = [];
        var series = [];

        DATA.categories.forEach(function (category) {
            category.groups.forEach(function (group) {
                var items = applyFilters(group.items, filters);

                if (items.length) {
                    (group.kind === "sketch" ? live : series).push({
                        category: category,
                        group: group,
                        items: items
                    });
                }
            });
        });

        return live.concat(series);
    }

    function renderWorldSection(section) {
        var category = section.category;
        var group = section.group;
        var items = section.items;
        var fragment = document.createDocumentFragment();

        fragment.appendChild(
            el("div", { class: "section-head" }, [
                el("h2", {}, [
                    el("a", {
                        href: buildHash([category.id, group.id]),
                        text: category.title + " · " + group.title
                    })
                ]),
                el("span", {
                    class: "count",
                    text:
                        items.length === group.items.length
                            ? plural(items.length, "piece")
                            : items.length +
                              " of " +
                              plural(group.items.length, "piece")
                })
            ])
        );

        // A series says once what all its pieces share. Sketch cards say it
        // for themselves.
        var shared = group.kind === "sketch" ? null : sharedTaxonomy(items);

        if (shared) {
            fragment.appendChild(taxonomyLine(shared));

            if (shared.concept) {
                fragment.appendChild(
                    el("p", { class: "section-blurb", text: shared.concept })
                );
            }
        }

        fragment.appendChild(createItemGrid(group, items, true));

        return fragment;
    }

    function renderWorlds(params) {
        renderBreadcrumb([
            { label: "creative coding", href: "#/" },
            { label: "worlds" }
        ]);
        renderNav(WORLDS_ROUTE);
        visibleItems = [];

        var filters = activeFilters(WORLD_FACETS, params);

        // A row with a single value can't narrow anything, unless a link
        // arrived with that filter set and needs a way to clear it.
        var facets = WORLD_FACETS.filter(function (facet) {
            return facet.values.length > 1 || params.has(facet.key);
        });

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: "worlds" }),
                el("p", {
                    text:
                        "every piece from every toolkit, by the world it " +
                        "belongs to. a piece can belong to several worlds " +
                        "and is shown once."
                })
            ])
        );

        var controls = createFacetControls(
            facets,
            params,
            [WORLDS_ROUTE],
            PIECES.map(function (piece) {
                return piece.item;
            })
        );

        if (controls) {
            view.appendChild(controls);
        }

        var world = findById(VOCABULARY.worlds, filters.world);

        if (world) {
            view.appendChild(
                el("p", { class: "world-note" }, [
                    el("strong", { text: world.id }),
                    document.createTextNode(
                        world.identity + ". it explores " + world.concepts + "."
                    )
                ])
            );
        }

        var sections = worldSections(filters);

        if (!sections.length) {
            view.appendChild(
                el("p", {
                    class: "empty",
                    text: world && !worldHasPieces(world)
                        ? "nothing in this world yet."
                        : "nothing matches this filter."
                })
            );
            return;
        }

        sections.forEach(function (section) {
            view.appendChild(renderWorldSection(section));
        });
    }

    /* ------------------------------------------------------------ pieces */

    // A series whose pieces share one taxonomy counts as one candidate, so
    // the 126 render engine images don't crowd out everything else. A
    // sketch, or a piece of a mixed series, counts on its own.
    function buildRelatedCandidates() {
        var candidates = [];

        DATA.categories.forEach(function (category) {
            category.groups.forEach(function (group) {
                var shared =
                    group.kind === "sketch" ? null : sharedTaxonomy(group.items);

                if (shared) {
                    candidates.push({
                        items: group.items,
                        taxonomy: shared,
                        cover: group.items[0],
                        href: buildHash([category.id, group.id]),
                        title: category.title + " · " + group.title,
                        note: plural(group.items.length, "piece")
                    });
                    return;
                }

                group.items.forEach(function (item) {
                    candidates.push({
                        items: [item],
                        taxonomy: item.taxonomy,
                        cover: item,
                        href: pieceHash(item),
                        title: item.title,
                        note:
                            item.kind === "sketch"
                                ? "live sketch"
                                : category.title + " · " + group.title
                    });
                });
            });
        });

        return candidates;
    }

    var RELATED_CANDIDATES = buildRelatedCandidates();

    // Ranked by how many worlds, systems and interactions they share with
    // the piece, then by data order. A plain count, not a recommender.
    function relatedTo(item) {
        var tags = tagsOf(item.taxonomy);

        return RELATED_CANDIDATES.map(function (candidate, order) {
            return {
                candidate: candidate,
                order: order,
                shared:
                    candidate.items.indexOf(item) === -1
                        ? tagsOf(candidate.taxonomy).filter(function (tag) {
                              return tags.indexOf(tag) !== -1;
                          })
                        : []
            };
        })
            .filter(function (match) {
                return match.shared.length > 0;
            })
            .sort(function (a, b) {
                return b.shared.length - a.shared.length || a.order - b.order;
            })
            .slice(0, RELATED_LIMIT);
    }

    function createRelated(item) {
        var matches = relatedTo(item);

        if (!matches.length) {
            return null;
        }

        return el("section", { class: "related" }, [
            el("h2", { text: "related" }),
            el("p", {
                class: "section-blurb",
                text:
                    "pieces that share a world, system or interaction with " +
                    "this one."
            }),
            el(
                "div",
                { class: "related-grid" },
                matches.map(function (match) {
                    var candidate = match.candidate;

                    return el(
                        "a",
                        { class: "related-card", href: candidate.href },
                        [
                            candidate.cover.thumb
                                ? el("img", {
                                      src: candidate.cover.thumb,
                                      alt: "",
                                      loading: "lazy"
                                  })
                                : el("div", {
                                      class: "cover-placeholder",
                                      text: "▶"
                                  }),
                            el("div", { class: "body" }, [
                                el("div", {
                                    class: "related-title",
                                    text: candidate.title
                                }),
                                el("div", {
                                    class: "related-meta",
                                    text: candidate.note
                                }),
                                el("div", {
                                    class: "related-meta",
                                    text:
                                        "shares " +
                                        match.shared.map(tagLabel).join(", ")
                                })
                            ])
                        ]
                    );
                })
            )
        ]);
    }

    function createFact(label, nodes) {
        return [
            el("dt", { text: label }),
            el("dd", {}, nodes)
        ];
    }

    function tagChips(key, values, primary) {
        return values.map(function (value) {
            return tagLink(
                key,
                value,
                "chip" + (value === primary ? " primary" : "")
            );
        });
    }

    function externalLink(href, text) {
        return el("a", {
            href: href,
            target: "_blank",
            rel: "noopener",
            text: text
        });
    }

    function renderPiece(piece) {
        var item = piece.item;
        var category = piece.category;
        var group = piece.group;
        var taxonomy = item.taxonomy;

        renderBreadcrumb([
            { label: "creative coding", href: "#/" },
            { label: "worlds", href: buildHash([WORLDS_ROUTE]) },
            { label: item.title }
        ]);
        renderNav(WORLDS_ROUTE);
        visibleItems = item.kind === "sketch" ? [] : [item];

        var preview;

        if (item.kind === "sketch") {
            preview = createSketchFrame(item);
        } else {
            var image = el("img", { src: item.thumb, alt: item.title });

            if (item.width && item.height) {
                image.style.aspectRatio = item.width + " / " + item.height;
            }

            preview = el(
                "button",
                {
                    class: "piece-image",
                    type: "button",
                    "aria-label": "view larger",
                    onclick: function () {
                        openLightbox(0);
                    }
                },
                [image]
            );
        }

        var facts = [];

        if (taxonomy) {
            facts = facts.concat(
                createFact(
                    "world",
                    tagChips(
                        "world",
                        [taxonomy.world].concat(taxonomy.worlds),
                        taxonomy.world
                    )
                )
            );

            if (taxonomy.systems.length) {
                facts = facts.concat(
                    createFact("system", tagChips("system", taxonomy.systems))
                );
            }

            if (taxonomy.interactions.length) {
                facts = facts.concat(
                    createFact(
                        "interaction",
                        tagChips("interaction", taxonomy.interactions)
                    )
                );
            }

            if (taxonomy.modes.length) {
                facts = facts.concat(
                    createFact("mode", [
                        document.createTextNode(taxonomy.modes.join(", "))
                    ])
                );
            }
        } else {
            facts = facts.concat(
                createFact("world", [document.createTextNode("unclassified")])
            );
        }

        facts = facts.concat(
            createFact("series", [
                el("a", {
                    href: buildHash([category.id, group.id]),
                    text: category.title + " · " + group.title
                }),
                document.createTextNode(
                    "  ·  " + plural(group.items.length, "piece")
                )
            ])
        );

        var file = [];

        if (item.width) {
            file.push(
                document.createTextNode(
                    item.width +
                        " × " +
                        item.height +
                        "  ·  " +
                        formatBytes(item.bytes) +
                        "  ·  "
                )
            );
            file.push(externalLink(item.full, "full size ↗"));
        } else {
            file.push(externalLink(item.full, "open ↗"));
        }

        if (item.source && item.source !== item.full) {
            file.push(document.createTextNode("  ·  "));
            file.push(externalLink(item.source, item.sourceLabel + " ↗"));
        }

        facts = facts.concat(createFact("file", file));

        clear(view);
        view.appendChild(
            el("article", { class: "piece" }, [
                el("div", { class: "piece-preview" }, [preview]),
                el("div", { class: "piece-info" }, [
                    el("h1", { text: item.title }),
                    taxonomy && taxonomy.concept
                        ? el("p", {
                              class: "piece-concept",
                              text: taxonomy.concept
                          })
                        : null,
                    el("dl", { class: "piece-facts" }, facts)
                ])
            ])
        );

        var related = createRelated(item);

        if (related) {
            view.appendChild(related);
        }
    }

    function renderMissingPiece(id) {
        renderBreadcrumb([
            { label: "creative coding", href: "#/" },
            { label: "worlds", href: buildHash([WORLDS_ROUTE]) },
            { label: "not found" }
        ]);
        renderNav(WORLDS_ROUTE);
        visibleItems = [];

        clear(view);
        view.appendChild(
            el("div", { class: "page-head" }, [
                el("h1", { text: "not found" }),
                el("p", {}, [
                    document.createTextNode(
                        "no piece has the id “" + id + "”. "
                    ),
                    el("a", {
                        href: buildHash([WORLDS_ROUTE]),
                        text: "browse every world"
                    })
                ])
            ])
        );
    }

    /* ------------------------------------------------------------ render */

    // Gives focus back to the chip that was used, after the view has been
    // rebuilt, so keyboard users keep their place while filtering.
    function restoreChipFocus(chip) {
        Array.prototype.some.call(
            view.querySelectorAll("[data-chip]"),
            function (node) {
                if (node.getAttribute("data-chip") === chip) {
                    node.focus();
                    return true;
                }

                return false;
            }
        );
    }

    function render() {
        var route = parseRoute();
        var category = findCategory(route.segments[0]);

        var focused = document.activeElement;
        var chip =
            focused && focused.getAttribute
                ? focused.getAttribute("data-chip")
                : null;

        closeLightbox();

        if (route.segments[0] === WORLDS_ROUTE) {
            if (route.segments.length > 1) {
                var piece = PIECE_BY_ID[route.segments[1]];

                if (piece) {
                    renderPiece(piece);
                } else {
                    renderMissingPiece(route.segments[1]);
                }
            } else {
                renderWorlds(route.params);
            }
        } else if (!category) {
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

        if (chip !== null) {
            restoreChipFocus(chip);
        }
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

        // Every piece has a page of its own, unless that is where we are.
        var route = parseRoute();

        if (route.segments[0] !== WORLDS_ROUTE || route.segments[1] !== item.id) {
            lightboxCaption.appendChild(
                el("span", {}, [
                    el("a", { href: pieceHash(item), text: "about this piece" })
                ])
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

        // With one image there is nothing to step through.
        lightbox.classList.toggle("single", visibleItems.length < 2);

        lightbox.hidden = false;
        document.body.style.overflow = "hidden";
        document.getElementById("lightbox-close").focus();
    }

    // Keeps Tab inside the open lightbox, wrapping at either end.
    function trapFocus(event) {
        var focusable = Array.prototype.filter.call(
            lightbox.querySelectorAll("button, a[href]"),
            function (node) {
                return node.offsetParent !== null;
            }
        );

        if (!focusable.length) {
            return;
        }

        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        var current = document.activeElement;
        var inside = lightbox.contains(current);

        if (event.shiftKey && (current === first || !inside)) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && (current === last || !inside)) {
            event.preventDefault();
            first.focus();
        }
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
        } else if (event.key === "Tab") {
            trapFocus(event);
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
