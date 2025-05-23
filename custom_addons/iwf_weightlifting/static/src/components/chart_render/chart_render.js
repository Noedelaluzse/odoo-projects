/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUpdateProps, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class ChartRender extends Component {
  setup() {
    this.chartRef = useRef("chart");
    this.chartInstance = null;

    onWillStart(async () => {
      await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js");
    });

    onMounted(() => this.renderChart());
    onWillUpdateProps(() => this.renderChart());
  }

  renderChart() {
    const ctx = this.chartRef.el;
    if (!ctx || !window.Chart) return;

    console.log("Rendering chart:", this.props.title, this.props.data);

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    this.chartInstance = new Chart(ctx, {
      type: this.props.type || "bar",
      data: this.props.data || {
        labels: [],
        datasets: [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
          },
          title: {
            display: !!this.props.title,
            text: this.props.title || "",
          },
        },
      },
    });
  }
}

ChartRender.template = "iwf_weightlifting.ChartRender";

ChartRender.props = {
  type: String,
  title: { type: String, optional: true },
  data: Object,
};