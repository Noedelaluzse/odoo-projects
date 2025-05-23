/** @odoo-module */

import { Component, onWillStart, useRef, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { KpiCard } from "./kpi_card/kpi_card";
import { ChartRender } from "./chart_render/chart_render";
import { useService } from "@web/core/utils/hooks";
//import moment from './moment.min'
export class DashboardOrganizer extends Component {
  setup() {
    const savedPeriod = parseInt(
      localStorage.getItem("dashboard_period") || "90"
    );

    this.state = useState({
      quotations: {
        value: 10,
        percentage: 6,
      },
      period: savedPeriod,
    });

    this.orm = useService("orm");
    this.actionService = useService("action");

    onWillStart(async () => {
      await loadJS(
        "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"
      );
      this.getDates();
      await this.getQuotations();
      await this.getOrders();
    });
  }

  async onChangePeriod() {
    localStorage.setItem("dashboard_period", this.state.period);
    this.getDates();
    await this.getQuotations();
    await this.getOrders();
  }

  getDates() {
    this.state.current_date = window
      .moment()
      .subtract(this.state.period, "days")
      .format("YYYY-MM-DD");
    this.state.previous_date = window
      .moment()
      .subtract(this.state.period * 2, "days")
      .format("YYYY-MM-DD");
  }

  async getQuotations() {
    let domain = [["state", "in", ["sent", "draft"]]];

    if (this.state.period > 0) {
      domain.push(["date_order", ">", this.state.current_date]);
    }
    const data = await this.orm.searchCount("sale.order", domain);
    this.state.quotations.value = data;

    // previous period
    let pre_domain = [["state", "in", ["sent", "draft"]]];

    if (this.state.period > 0) {
      pre_domain.push(
        ["date_order", ">", this.state.previous_date],
        ["date_order", "<=", this.state.current_date]
      );
    }
    const prev_data = await this.orm.searchCount("sale.order", pre_domain);

    let percentage = 0;

    if (prev_data > 0) {
      percentage = ((data - prev_data) / prev_data) * 100;
    } else if (data > 0) {
      percentage = 100; // hubo un aumento desde 0
    } else {
      percentage = 0; // sin cambio
    }

    this.state.quotations.percentage = percentage.toFixed(2);
  }

  async getOrders() {
    let domain = [["state", "in", ["sale", "done"]]];

    if (this.state.period > 0) {
      domain.push(["date_order", ">", this.state.current_date]);
    }
    const data = await this.orm.searchCount("sale.order", domain);
    //this.state.quotations.value = data

    // previous period
    let pre_domain = [["state", "in", ["sale", "done"]]];

    if (this.state.period > 0) {
      pre_domain.push(
        ["date_order", ">", this.state.previous_date],
        ["date_order", "<=", this.state.current_date]
      );
    }
    const prev_data = await this.orm.searchCount("sale.order", pre_domain);

    let percentage = 0;

    if (prev_data > 0) {
      percentage = ((data - prev_data) / prev_data) * 100;
    } else if (data > 0) {
      percentage = 100; // hubo un aumento desde 0
    } else {
      percentage = 0; // sin cambio
    }

    //this.state.quotations.percentage = percentage.toFixed(2);

    // revenues
    const current_revenue = await this.orm.readGroup(
      "sale.order",
      domain,
      ["amount_total:sum"],
      []
    );
    const prev_revenue = await this.orm.readGroup(
      "sale.order",
      pre_domain,
      ["amount_total:sum"],
      []
    );
    const revenue_percentage =
      ((current_revenue[0].amount_total - prev_revenue[0].amount_total) /
        prev_revenue[0].amount_total) *
      100;

    // average
    const current_average = await this.orm.readGroup(
      "sale.order",
      domain,
      ["amount_total:avg"],
      []
    );
    const prev_average = await this.orm.readGroup(
      "sale.order",
      pre_domain,
      ["amount_total:avg"],
      []
    );
    const average_percentage =
      ((current_average[0].amount_total - prev_average[0].amount_total) /
        prev_average[0].amount_total) *
      100;

    this.state.orders = {
      value: data,
      percentage: percentage.toFixed(2),
      revenue: `$${(current_revenue[0].amount_total / 1000).toFixed(2)}K`,
      revenue_percentage: revenue_percentage.toFixed(2),
      average: `$${(current_average[0].amount_total / 1000).toFixed(2)}K`,
      average_percentage: average_percentage.toFixed(2),
    };
  }

  async viewQuotations() {
    let domain = [["state", "in", ["sent", "draft"]]];
    if (this.state.period > 0) {
      domain.push(["date_order", ">", this.state.current_date]);
    }

    // Buscar el ID de la vista por xml_id desde ir.model.data
    const list_view = await this.orm.searchRead(
      "ir.model.data",
      [
        ["name", "=", "view_quotation_list_with_onboarding"],
        ["model", "=", "ir.ui.view"],
        ["module", "=", "sale"], // Ajusta esto al nombre del módulo correcto si es diferente
      ],
      ["res_id"]
    );
    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Quotations",
      res_model: "sale.order",
      domain: domain,
      views: [
        [list_view.length > 0 ? list_view[0].res_id : false, "list"],
        [false, "form"],
      ],
    });
  }

  viewOrders() {
    let domain = [["state", "in", ["sale", "done"]]];
    if (this.state.period > 0) {
      domain.push(["date_order", ">", this.state.current_date]);
    }

    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Quotations",
      res_model: "sale.order",
      domain: domain,
      context: { group_by: ["date_order"] },
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }

  viewRevenues() {
    let domain = [["state", "in", ["sale", "done"]]];
    if (this.state.period > 0) {
      domain.push(["date_order", ">", this.state.current_date]);
    }

    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Quotations",
      res_model: "sale.order",
      domain: domain,
      context: { group_by: ["date_order"] },
      views: [
        [false, "pivot"],
        [false, "form"],
      ],
    });
  }

  viewTopProducts() {
    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Top Products",
      res_model: "sale.order.line",
      views: [
        [false, "list"],
        [false, "form"],
      ],
      domain: [], // puedes aplicar filtros si los deseas
    });
  }

  viewTopSales() {
    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Top Sales People",
      res_model: "res.users", // o el modelo correcto para vendedores
      views: [
        [false, "list"],
        [false, "form"],
      ],
      domain: [],
    });
  }

  viewMonthlySales() {
    this.viewOrders(); // o una versión filtrada más específica si quieres
  }

  viewPartnerOrders() {
    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: "Partners Orders",
      res_model: "res.partner",
      views: [
        [false, "list"],
        [false, "form"],
      ],
      domain: [],
    });
  }
}

DashboardOrganizer.template = "iwf_weightlifting.DashboardOrganizer";
DashboardOrganizer.components = { KpiCard, ChartRender };
registry
  .category("actions")
  .add("iwf_weightlifting.dashboard_organizer", DashboardOrganizer);
