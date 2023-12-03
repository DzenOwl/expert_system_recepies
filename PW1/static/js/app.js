const localFacts = JSON.parse(localStorage.getItem('facts'))
const localRules = JSON.parse(localStorage.getItem('rules'))

function getCheckedFacts() {
    return Array.from(document.querySelectorAll("[id^=fact-]")).filter(item => item.checked);
}

function getIdNum(id) {
    const split = id.split("-")
    return parseInt(split[split.length - 1])
}

let vueApp = new Vue({
    el: "#app",
    data: {
        facts: localFacts,
        rules: localRules,

        ingredients: [],
        machineResults: null,
        machineResultsExplained: null,
        activeRule: -1,
    },
    computed: {
        allFacts: function () {
            if (this.machineResults === null)
                return Array.from(new Set(this.ingredients)).sort();
            else
                return Array.from(new Set(this.ingredients.concat(this.machineResults))).sort();
        }
    },
    methods: {
        importDb: function () {
            let uploadAnchorNode = document.createElement('input');
            uploadAnchorNode.setAttribute("type", "file");
            uploadAnchorNode.setAttribute("accept", "application/JSON");
            uploadAnchorNode.style.display = "none";

            uploadAnchorNode.onchange = (event) => {
                const jsonFile = event.target.files[0];
                const fr = new FileReader();
                fr.onload = (event) => {
                    const dataJson = JSON.parse(event.target.result);
                    this.facts = dataJson.facts;
                    this.rules = dataJson.rules;
                }
                fr.readAsText(jsonFile);
            };

            document.body.appendChild(uploadAnchorNode);

            uploadAnchorNode.click();
        },
        exportDb: function () {
            const data = {
                facts: this.facts,
                rules: this.rules,
            }
            const dataStr = `data:text/json;charset=utf-8,${
                encodeURIComponent(JSON.stringify(data))}`;

            let downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "recipes.json");
            downloadAnchorNode.style.display = "none";
            document.body.appendChild(downloadAnchorNode);

            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        },
        addFact: function () {
            let factInput = document.getElementById("fact-input-add");
            let fact = factInput.value;

            if (fact === "")
                return

            if (!this.facts.includes(fact))
                this.facts.push(fact);

            factInput.value = "";
        },
        addRule: function () {
            let selectedFactsElement = getCheckedFacts();
            let selectedFactsIndexes = selectedFactsElement.map(item => getIdNum(item.id));
            const selectedFacts = this.facts.filter((_, i) => selectedFactsIndexes.includes(i));

            let ruleElement = document.getElementById("rule-input-add");
            let ruleName = ruleElement.value;

            if (ruleName === "" || selectedFactsIndexes.length === 0)
                return;

            if (!this.facts.includes(ruleName))
                return;

            if (selectedFacts.includes(ruleName))
                return;

            this.rules.push({
                rule: ruleName,
                facts: selectedFacts,
            });

            selectedFactsElement.forEach(item => item.checked = false);
            ruleElement.value = "";
        },
        deleteFacts: function () {
            let selectedFacts = getCheckedFacts();
            let selectedFactsIndexes = selectedFacts.map(item => getIdNum(item.id));

            this.facts = this.facts.filter((_, i) => !selectedFactsIndexes.includes(i));

            selectedFacts.forEach(item => item.checked = false);
        },
        deleteRule: function () {
            let selectedRule = Array.from(document.querySelectorAll("[id^=rule-]")).find(item => item.checked);
            let selectedRuleIndex = getIdNum(selectedRule.id);
            this.rules.splice(selectedRuleIndex, 1);
        },
        runMachine: function () {
            const factsDict = this.facts.reduce((acc, cur, i) => {
                return {...acc, [i + 1]: cur}
            }, {});

            const selectedFactsElement = getCheckedFacts();
            const factToNum = Object.fromEntries(Object.entries(factsDict).map(a => a.reverse()));

            const selectedFactsIndexes = selectedFactsElement.map(item => getIdNum(item.id));
            const selectedFacts = this.facts.filter((_, i) => selectedFactsIndexes.includes(i));
            const selectedFactsId = selectedFacts.map(fact => factToNum[fact]);

            // this.rules.reduce((acc, cur, i) => Object.assign(
            //     {},
            //     acc,
            //     {
            //         [i + 1]: [
            //             factToNum[cur.rule],
            //             cur.facts.map(fact => factToNum[fact])
            //         ]
            //     }), {});

            const rulesDict = Object.fromEntries(
                this.rules.map((cur, i) => [i + 1, [
                    factToNum[cur.rule],
                    cur.facts.map(fact => factToNum[fact])
                ]])
            )
            //
            // const rulesDict = this.rules.reduce((acc, cur, i) => ({
            //     ...acc,
            //     [i + 1]: [
            //         factToNum[cur.rule],
            //         cur.facts.map(fact => factToNum[fact])
            //     ]
            // }), {});

            const jsonBody = JSON.stringify({
                facts: factsDict,
                rules: rulesDict,
                selected: selectedFactsId,
            });

            fetch('/machine', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: jsonBody
            })
                .then(response => response.json())
                .then(commits => {
                    if (commits.error) throw new Error("Commits are empty");
                    return commits
                })
                .then(({new_facts, new_facts_explained}) => {
                    this.machineResults = new_facts
                    this.machineResultsExplained = new_facts_explained
                })
                .catch((err) => console.error(err))
        },
        toggleAvailableFact: function (event) {
            if (event.target.checked)
                this.ingredients.push(this.facts[getIdNum(event.target.id)]);
            else
                this.ingredients = this.ingredients.filter(i => i !== this.facts[getIdNum(event.target.id)]);
        }
    }
});