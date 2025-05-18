/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DashboardOrganizer extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            totalAthletes: 0,
            totalAttempts: 0,
            totalPenalties: 0,
        });

        onWillStart(async () => {
            const [athletes, attempts, penalties] = await Promise.all([
                this.orm.searchCount("iwf.athlete", []),
                this.orm.searchCount("iwf.lift_attempt", []),
                this.orm.searchCount("iwf.penalty", []),
            ]);
            this.state.totalAthletes = athletes;
            this.state.totalAttempts = attempts;
            this.state.totalPenalties = penalties;
        });
    }

    static template = "iwf_weightlifting.DashboardOrganizer";
}

registry.category("actions").add("iwf_dashboard.organizer", DashboardOrganizer);