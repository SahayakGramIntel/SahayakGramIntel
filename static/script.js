(function () {
    var demoBtn = document.getElementById("demo-btn");
    if (demoBtn) {
        demoBtn.addEventListener("click", function () {
            document.getElementById("name").value = "Ramesh";
            document.getElementById("location").value = "Mandsaur";
            document.getElementById("business_idea").value = "Dairy and milk products";
            document.getElementById("investment").value = "300000";
            document.getElementById("monthly_sales").value = "70000";
            document.getElementById("monthly_expenses").value = "45000";
            document.getElementById("loan_amount").value = "150000";
            document.getElementById("interest_rate").value = "10";
            document.getElementById("loan_tenure").value = "36";
        });
    }

    function money(n) {
        var v = Number(n);
        if (isNaN(v)) return n;
        return "₹" + v.toLocaleString("en-IN", { maximumFractionDigits: 2 });
    }

    var buttons = document.querySelectorAll(".whatif-btn");
    if (buttons.length && window.GRAMINTEL_ASSESSMENT_ID) {
        buttons.forEach(function (btn) {
            btn.addEventListener("click", function () {
                fetch("/api/what-if", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        assessment_id: window.GRAMINTEL_ASSESSMENT_ID,
                        scenario: btn.getAttribute("data-scenario")
                    })
                })
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        if (data.error) {
                            alert(data.error);
                            return;
                        }
                        document.getElementById("whatif-result").hidden = false;
                        document.getElementById("whatif-label").textContent = data.label;
                        document.getElementById("old-revenue").textContent = money(data.old_revenue);
                        document.getElementById("new-revenue").textContent = money(data.new_revenue);
                        document.getElementById("diff-revenue").textContent = money(data.difference.revenue);
                        document.getElementById("old-expenses").textContent = money(data.old_expenses);
                        document.getElementById("new-expenses").textContent = money(data.new_expenses);
                        document.getElementById("diff-expenses").textContent = money(data.difference.expenses);
                        document.getElementById("old-profit").textContent = money(data.old_profit);
                        document.getElementById("new-profit").textContent = money(data.new_profit);
                        document.getElementById("diff-profit").textContent = money(data.difference.profit);
                        document.getElementById("old-emi").textContent = money(data.old_emi);
                        document.getElementById("new-emi").textContent = money(data.new_emi);
                        document.getElementById("diff-emi").textContent = money(data.difference.emi);
                        document.getElementById("old-feas").textContent = data.old_feasibility + " (" + data.old_band + ")";
                        document.getElementById("new-feas").textContent = data.new_feasibility + " (" + data.new_band + ")";
                        document.getElementById("diff-feas").textContent = data.difference.feasibility_score;
                    })
                    .catch(function () {
                        alert("Could not run the simulation. Please try again.");
                    });
            });
        });
    }
})();
