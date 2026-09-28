async function api(url, options = {}) {

    const response = await fetch(
        url,
        {
            credentials: "include",
            ...options
        }
    );

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {

        throw new Error(
            data.detail || "Request failed"
        );
    }

    return data;
}


function showError(error) {

    const box =
        document.getElementById(
            "form-error"
        );

    if (box) {

        box.textContent =
            error.message;

    } else {

        alert(error.message);
    }
}


async function logout() {

    await api(
        "/api/logout",
        {
            method: "POST"
        }
    );

    location.href = "/";
}


function bindLogin() {

    const form =
        document.getElementById(
            "login-form"
        );

    if (!form) return;

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            try {

                await api(
                    "/api/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            Object.fromEntries(
                                new FormData(form)
                            )
                        )
                    }
                );

                location.href =
                    "/dashboard";

            } catch (error) {

                showError(error);
            }
        }
    );
}


function bindRegister() {

    const form =
        document.getElementById(
            "register-form"
        );

    if (!form) return;

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            try {

                const payload =
                    Object.fromEntries(
                        new FormData(form)
                    );

                await api(
                    "/api/register",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            payload
                        )
                    }
                );

                await api(
                    "/api/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            {
                                email:
                                    payload.email,

                                password:
                                    payload.password
                            }
                        )
                    }
                );

                location.href =
                    "/dashboard";

            } catch (error) {

                showError(error);
            }
        }
    );
}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        function (character) {

            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[character];
        }
    );
}


function money(value) {

    return Number(
        value || 0
    ).toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 0
        }
    );
}


function renderResult(data) {

    const element =
        document.getElementById(
            "result"
        );

    element.innerHTML = `

        <section class="card">

            <div class="result-head">

                <div>

                    <span class="eyebrow">
                        AI PLAN
                    </span>

                    <h2>
                        ${escapeHtml(
                            data.summary
                        )}
                    </h2>

                </div>


                <div>

                    <div class="metric">
                        ₹${money(
                            data.estimated_total
                        )}
                    </div>

                    <small class="muted">
                        estimated total
                    </small>

                </div>

            </div>


            <p>

                <strong>
                    Budget:
                </strong>

                ₹${money(
                    data.budget_total
                )}

                &nbsp;

                <strong>
                    Remaining:
                </strong>

                ₹${money(
                    data.budget_remaining
                )}

            </p>


            <h3>
                Budget allocation
            </h3>


            <div class="alloc">

                ${data.allocations
                    .map(
                        function (allocation) {

                            return `

                                <div class="alloc-row">

                                    <span>
                                        ${escapeHtml(
                                            allocation.category
                                        )}
                                    </span>

                                    <div class="bar">

                                        <span
                                            style="width:${allocation.percentage}%"
                                        ></span>

                                    </div>

                                    <strong>
                                        ₹${money(
                                            allocation.amount
                                        )}
                                    </strong>

                                </div>

                            `;
                        }
                    )
                    .join("")}

            </div>


            <h3>
                Recommendations
            </h3>


            <div class="recommendations">

                ${data.recommendations
                    .map(
                        function (recommendation) {

                            return `

                                <article class="rec">

                                    <span class="tag">

                                        ${escapeHtml(
                                            recommendation.platform
                                        )}

                                    </span>


                                    <h3>

                                        ${escapeHtml(
                                            recommendation.name
                                        )}

                                    </h3>


                                    <div class="price">

                                        ₹${money(
                                            recommendation.estimated_price
                                        )}

                                    </div>


                                    <p>

                                        ${escapeHtml(
                                            recommendation.reason
                                        )}

                                    </p>


                                    <a
                                        href="${recommendation.search_url}"
                                        target="_blank"
                                        rel="noopener"
                                    >

                                        Open platform search ↗

                                    </a>

                                </article>

                            `;
                        }
                    )
                    .join("")}

            </div>


            <h3>
                Tips
            </h3>


            <ul>

                ${data.tips
                    .map(
                        function (tip) {

                            return `
                                <li>
                                    ${escapeHtml(
                                        tip
                                    )}
                                </li>
                            `;
                        }
                    )
                    .join("")}

            </ul>

        </section>

    `;
}


function bindHomePlanner() {

    const form =
        document.getElementById(
            "home-form"
        );

    if (!form) return;


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const formData =
                new FormData(form);

            const items =
                formData
                    .get("items")
                    .split("\n")
                    .filter(Boolean)
                    .map(
                        function (line) {

                            const parts =
                                line
                                    .split("|")
                                    .map(
                                        function (
                                            value
                                        ) {
                                            return (
                                                value ||
                                                ""
                                            ).trim();
                                        }
                                    );

                            return {

                                name:
                                    parts[0] ||
                                    "item",

                                category:
                                    parts[0] ||
                                    "item",

                                quantity:
                                    Number(
                                        parts[1]
                                    ) || 1,

                                notes:
                                    parts[2] ||
                                    ""
                            };
                        }
                    );


            const payload = {

                budget:
                    Number(
                        formData.get(
                            "budget"
                        )
                    ),

                style:
                    formData.get(
                        "style"
                    ),

                city:
                    formData.get(
                        "city"
                    ),

                rooms:
                    formData
                        .get("rooms")
                        .split(",")
                        .map(
                            function (value) {
                                return value.trim();
                            }
                        )
                        .filter(Boolean),

                items,

                priorities:
                    formData.get(
                        "priorities"
                    )
            };


            await runPlanner(
                "/api/generate-home",
                payload
            );
        }
    );
}


function bindPartyPlanner() {

    const form =
        document.getElementById(
            "party-form"
        );

    if (!form) return;


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const formData =
                new FormData(form);

            const payload =
                Object.fromEntries(
                    formData.entries()
                );

            payload.budget =
                Number(
                    payload.budget
                );

            payload.guests =
                Number(
                    payload.guests
                );


            await runPlanner(
                "/api/generate-party",
                payload
            );
        }
    );
}


function bindJewelryPlanner() {

    const form =
        document.getElementById(
            "jewelry-form"
        );

    if (!form) return;


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const formData =
                new FormData(form);

            try {

                document
                    .getElementById(
                        "result"
                    )
                    .innerHTML = `
                        <div class="card loading">
                            Generating your plan…
                        </div>
                    `;


                const data =
                    await api(
                        "/api/generate-jewelry",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                renderResult(data);

            } catch (error) {

                showError(error);
            }
        }
    );
}


async function runPlanner(
    url,
    payload
) {

    try {

        document
            .getElementById(
                "result"
            )
            .innerHTML = `
                <div class="card loading">
                    Generating your plan…
                </div>
            `;


        const data =
            await api(
                url,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        renderResult(data);

    } catch (error) {

        showError(error);
    }
}


async function loadHistory() {

    const element =
        document.getElementById(
            "history"
        );

    if (!element) return;


    try {

        const rows =
            await api(
                "/api/history"
            );


        if (!rows.length) {

            element.innerHTML = `
                <p class="muted">
                    No saved recommendations yet.
                </p>
            `;

            return;
        }


        element.innerHTML =
            rows
                .map(
                    function (row) {

                        return `

                            <div class="history-item">

                                <span class="tag">

                                    ${escapeHtml(
                                        row.planner
                                    )}

                                </span>


                                <h3>

                                    ${escapeHtml(
                                        row.title
                                    )}

                                </h3>


                                <small class="muted">

                                    ${new Date(
                                        row.created_at
                                    ).toLocaleString()}

                                </small>

                            </div>

                        `;
                    }
                )
                .join("");

    } catch (error) {

        element.innerHTML = `

            <p class="error">

                ${escapeHtml(
                    error.message
                )}

            </p>

        `;
    }
}