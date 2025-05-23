/** @odoo-module **/

import { Component } from "@odoo/owl";

export class KpiCard extends Component {
  triggerClick() {
    if (this.props.onClick) {
      this.props.onClick();
    }
  }
}

KpiCard.template = "iwf_weightlifting.KpiCard";
KpiCard.props = {
  name: String,
  value: [String, Number],
  percentage: { type: [Number, Boolean, null], optional: true },
  onClick: { type: Function, optional: true },
};