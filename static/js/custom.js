document.addEventListener("DOMContentLoaded", function() {

    // On this day: the strip shows one pick at a time, stepped by its arrows.
    var otd = document.getElementById("otd");
    if (otd) {
        var otdItems = Array.prototype.slice.call(otd.querySelectorAll(".otd-item"));
        if (otdItems.length > 1) {
            var otdIndex = 0;
            var otdPrevious = otd.querySelector(".otd-prev");
            var otdNext = otd.querySelector(".otd-next");
            var otdPosition = otd.querySelector(".otd-position");
            var showOtdItem = function(index) {
                otdIndex = (index + otdItems.length) % otdItems.length;
                otdItems.forEach(function(item, i) { item.hidden = i !== otdIndex; });
                otdPosition.textContent = (otdIndex + 1) + "/" + otdItems.length;
            };
            otd.classList.add("is-carousel");
            otdPrevious.hidden = false;
            otdNext.hidden = false;
            otdPosition.hidden = false;
            showOtdItem(0);
            otdPrevious.addEventListener("click", function() { showOtdItem(otdIndex - 1); });
            otdNext.addEventListener("click", function() { showOtdItem(otdIndex + 1); });
        }
    }

    // Header search: don't submit empty queries.
    var navSearch = document.getElementById("nav-search");
    if (navSearch) {
        var navSearchInput = navSearch.querySelector("input");
        navSearch.addEventListener("submit", function(e) {
            if (!navSearchInput.value.trim()) {
                e.preventDefault();
                navSearchInput.focus();
            }
        });
    }

    // Filter dropdowns submit on change.
    document.querySelectorAll("#competition-filter select, #transaction-filter select").forEach(function(sel) {
        sel.addEventListener("change", function() { sel.form.submit(); });
    });

    // Tabs: build the tab list from div[tab] panes, show one at a time.
    function makeTabs(tabsId, wrapperId) {
        var tabs = document.getElementById(tabsId);
        var wrapper = document.getElementById(wrapperId);
        if (!tabs || !wrapper) return;

        var panes = Array.prototype.filter.call(wrapper.children, function(div) {
            return div.hasAttribute("tab");
        });
        if (!panes.length) return;

        tabs.classList.add("tabbing");

        var items = [];
        panes.forEach(function(pane) {
            var name = pane.getAttribute("tab");
            var label = pane.getAttribute("tab-label") || name;
            var a = document.createElement("a");
            a.href = "#" + name;
            var li = document.createElement("li");
            li.textContent = label;
            a.appendChild(li);
            tabs.appendChild(a);
            items.push(li);

            a.addEventListener("click", function(e) {
                e.preventDefault();
                items.forEach(function(el) { el.classList.remove("active"); });
                li.classList.add("active");
                panes.forEach(function(p) { p.style.display = "none"; });
                pane.style.display = "";
            });
        });

        tabs.querySelector("a").click();
    }

    // Chart switches: both charts are rendered, the control shows one of them.
    // Without JS the first panel stands and the buttons do nothing visible.
    document.querySelectorAll(".chart-switcher").forEach(function(switcher) {
        var buttons = switcher.querySelectorAll(".chart-switch button");
        var panels = switcher.querySelectorAll("[data-chart-panel]");
        buttons.forEach(function(button) {
            button.addEventListener("click", function() {
                buttons.forEach(function(b) { b.classList.remove("active"); });
                button.classList.add("active");
                panels.forEach(function(panel) {
                    panel.hidden = panel.dataset.chartPanel !== button.dataset.chart;
                });
            });
        });
    });

    makeTabs("tabs", "tab_wrapper");
    makeTabs("subtabs", "subtab_wrapper");
    makeTabs("subtabs2", "subtab_wrapper2");

    // Column sorting on stats and standings tables.
    function cellValue(row, i) {
        var cell = row.cells[i];
        return cell ? cell.textContent.trim() : "";
    }

    function makeSortable(table) {
        var headers = table.querySelectorAll("thead th");
        headers.forEach(function(th, col) {
            th.addEventListener("click", function() {
                var tbody = table.tBodies[0];
                if (!tbody) return;
                var dir = th.dataset.sorted === "asc" ? -1 : 1;
                headers.forEach(function(h) { delete h.dataset.sorted; });
                th.dataset.sorted = dir === 1 ? "asc" : "desc";

                var rows = Array.prototype.slice.call(tbody.rows);
                rows.sort(function(a, b) {
                    var x = cellValue(a, col), y = cellValue(b, col);
                    var nx = parseFloat(x.replace(/,/g, "")), ny = parseFloat(y.replace(/,/g, ""));
                    if (!isNaN(nx) && !isNaN(ny)) return (nx - ny) * dir;
                    return x.localeCompare(y) * dir;
                });
                rows.forEach(function(r) { tbody.appendChild(r); });
            });
        });
    }

    document.querySelectorAll("table.stats, table.standings, table.transactions, table.sources").forEach(makeSortable);

    // Clubs timeline: clicking a season's column head re-ranks the rows by
    // that season's finishes, clubs without one keeping their place below;
    // clicking the season in force restores the order the chart came in.
    document.querySelectorAll(".timeline-chart svg").forEach(function(svg) {
        var rows = Array.prototype.slice.call(svg.querySelectorAll(".row"));
        var rowH = parseFloat(svg.dataset.rowH);
        var sorted = null;
        var rank = function(season) {
            var keys = rows.map(function(row, index) {
                var key = Infinity;
                if (season) {
                    var block = row.querySelector('.mark[data-season="' + season + '"]');
                    if (block && block.dataset.place) key = parseInt(block.dataset.place, 10);
                }
                return {index: index, key: key};
            });
            keys.sort(function(a, b) { return (a.key - b.key) || (a.index - b.index); });
            keys.forEach(function(entry, position) {
                rows[entry.index].style.transform = "translateY(" + ((position - entry.index) * rowH) + "px)";
            });
            svg.querySelectorAll("text.season").forEach(function(label) {
                label.classList.toggle("sorted", label.dataset.season === season);
            });
        };
        svg.querySelectorAll(".head").forEach(function(head) {
            head.addEventListener("click", function() {
                sorted = sorted === head.dataset.season ? null : head.dataset.season;
                rank(sorted);
            });
        });
    });

    // Hover capsules: a mark with data-tip shows its lines, split on "|", in
    // one shared box that follows the pointer.
    var tipMarks = document.querySelectorAll("[data-tip]");
    if (tipMarks.length) {
        var tip = document.createElement("div");
        tip.className = "chart-tip";
        tip.hidden = true;
        document.body.appendChild(tip);
        var placeTip = function(e) {
            tip.style.left = (e.pageX + 14) + "px";
            tip.style.top = (e.pageY + 14) + "px";
        };
        tipMarks.forEach(function(mark) {
            mark.addEventListener("mouseenter", function(e) {
                tip.textContent = "";
                mark.dataset.tip.split("|").forEach(function(line, i) {
                    var div = document.createElement("div");
                    if (i === 0) div.className = "tip-head";
                    div.textContent = line;
                    tip.appendChild(div);
                });
                tip.hidden = false;
                placeTip(e);
            });
            mark.addEventListener("mousemove", placeTip);
            mark.addEventListener("mouseleave", function() { tip.hidden = true; });
        });
    }

});
