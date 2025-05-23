/** @odoo-module */

import { Component, onWillStart, useRef, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";

export class ChartRender extends Component {
  setup() {
    this.chartRef = useRef("chart");
    onWillStart(async () => {
      await loadJS(
        "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
      );
    });
    onMounted(() => this.renderChart());

  }
  renderChart() {
      const data = [
    { year: 2010, count: 10 },
    { year: 2011, count: 20 },
    { year: 2012, count: 15 },
    { year: 2013, count: 25 },
    { year: 2014, count: 22 },
    { year: 2015, count: 30 },
    { year: 2016, count: 28 },
  ];
    new Chart(this.chartRef.el, {
      type: this.props.type,
      data: {
        labels: data.map((row) => row.year),
        datasets: [
          {
            label: "Acquisitions by year",
            data: data.map((row) => row.count),
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
          title: {
            display: true,
            text: this.props.title,
            position: "bottom",
          },
        },
      },
    });
  }
}

ChartRender.template = "iwf_weightlifting.ChartRender";
