document.addEventListener("DOMContentLoaded", function() {

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

    // Homepage history strip: show one editorial pick at a time.
    var otd = document.getElementById("otd");
    if (otd) {
        var otdItems = Array.prototype.slice.call(otd.querySelectorAll(".otd-item"));
        if (otdItems.length > 1) {
            var otdIndex = 0;
            var otdPrevious = otd.querySelector(".otd-prev");
            var otdNext = otd.querySelector(".otd-next");
            var otdPosition = otd.querySelector(".otd-position");

            function showOtdItem(index) {
                otdIndex = (index + otdItems.length) % otdItems.length;
                otdItems.forEach(function(item, i) { item.hidden = i !== otdIndex; });
                otdPosition.textContent = (otdIndex + 1) + "/" + otdItems.length;
            }

            otd.classList.add("is-carousel");
            otdPrevious.hidden = false;
            otdNext.hidden = false;
            otdPosition.hidden = false;
            showOtdItem(0);
            otdPrevious.addEventListener("click", function() { showOtdItem(otdIndex - 1); });
            otdNext.addEventListener("click", function() { showOtdItem(otdIndex + 1); });
        }
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

    document.querySelectorAll("table.stats, table.standings, table.transactions").forEach(makeSortable);

});
