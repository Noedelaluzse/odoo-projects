/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "./kpi_card/kpi_card";
import { ChartRender } from "./chart_render/chart_render";

export class DashboardOrganizer extends Component {
  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");

    this.state = useState({
      competitions: [],
      selectedCompetitionId: null,
      kpi: {
        total_athletes: 0,
        valid_lifts: 0,
        total_penalties: 0,
        total_medals: 0,
      },
      charts: {
        athletesByGender: { labels: [], datasets: [] },
        validInvalidLifts: { labels: ["Valid", "Invalid"], datasets: [] },
        medalsByCountry: { labels: [], datasets: [] },
        penaltiesByType: { labels: ["Technical", "Disciplinary", "Doping"], datasets: [] },
      },
    });

    onWillStart(async () => {
      await this.loadCompetitions();
      if (this.state.competitions.length > 0) {
        this.state.selectedCompetitionId = this.state.competitions[0].id;
        await this.loadDashboardData();
      }
    });
  }

  async onChangeCompetition(ev) {
    this.state.selectedCompetitionId = parseInt(ev.target.value);
    await this.loadDashboardData();
  }

  async loadCompetitions() {
    const comps = await this.orm.searchRead("iwf.competition", [], ["id", "name"]);
    this.state.competitions = comps;
  }

  async loadDashboardData() {
    const compId = this.state.selectedCompetitionId;
    if (!compId) return;

    const [
      participations,
      validLifts,
      invalidLifts,
      penalties,
      results,
    ] = await Promise.all([
      this.orm.searchRead("iwf.participation", [["competition_id", "=", compId]], ["athlete_id"]),
      this.orm.searchCount("iwf.lift_attempt", [["competition_id", "=", compId], ["status", "=", "valid"]]),
      this.orm.searchCount("iwf.lift_attempt", [["competition_id", "=", compId], ["status", "!=", "valid"]]),
      this.orm.searchRead("iwf.penalty", [["competition_id", "=", compId]], ["type"]),
      this.orm.searchRead("iwf.result", [["competition_id", "=", compId], ["medal", "!=", false]], ["athlete_id"]),
    ]);

    // KPIs
    this.state.kpi.total_athletes = participations.length;
    this.state.kpi.valid_lifts = validLifts;
    this.state.kpi.total_penalties = penalties.length;
    this.state.kpi.total_medals = results.length;

    // Athletes by Gender
    const genderMap = { male: 0, female: 0 };
    for (const part of participations) {
      const [athlete] = await this.orm.read("iwf.athlete", [part.athlete_id[0]], ["gender"]);
      if (athlete && genderMap[athlete.gender] !== undefined) {
        genderMap[athlete.gender] += 1;
      }
    }

    this.state.charts.athletesByGender = structuredClone({
      labels: ["Male", "Female"],
      datasets: [{
        label: "Athletes",
        data: [genderMap.male, genderMap.female],
        backgroundColor: ["#36A2EB", "#FF6384"],
      }],
    });

    // Penalties by Type
    const penaltyMap = { technical: 0, disciplinary: 0, doping: 0 };
    for (const p of penalties) {
      if (penaltyMap[p.type] !== undefined) {
        penaltyMap[p.type] += 1;
      }
    }

    this.state.charts.penaltiesByType = structuredClone({
      labels: ["Technical", "Disciplinary", "Doping"],
      datasets: [{
        label: "Penalties",
        data: [penaltyMap.technical, penaltyMap.disciplinary, penaltyMap.doping],
        backgroundColor: ["#FFC107", "#17A2B8", "#DC3545"],
      }],
    });

    // Medals by Country
    const countryMap = {};
    for (const res of results) {
      const [athlete] = await this.orm.read("iwf.athlete", [res.athlete_id[0]], ["country_id"]);
      const countryName = athlete?.country_id?.[1] || "Unknown";
      countryMap[countryName] = (countryMap[countryName] || 0) + 1;
    }

    const countryLabels = Object.keys(countryMap);
    const countryData = Object.values(countryMap);
    const countryColors = countryLabels.map((_, i) => `hsl(${(i * 67) % 360}, 70%, 60%)`);

    this.state.charts.medalsByCountry = structuredClone({
      labels: countryLabels,
      datasets: [{
        label: "Medals",
        data: countryData,
        backgroundColor: countryColors,
      }],
    });

    // Valid vs Invalid Lifts
    this.state.charts.validInvalidLifts = structuredClone({
      labels: ["Valid", "Invalid"],
      datasets: [{
        label: "Lifts",
        data: [validLifts, invalidLifts],
        backgroundColor: ["#4CAF50", "#F44336"],
      }],
    });
  }

  viewAthletes() {
    this.actionService.doAction("base.action_res_partner_form");
  }

  viewLifts() {
    this.actionService.doAction("iwf_weightlifting.action_lift_attempts");
  }

  viewPenalties() {
    this.actionService.doAction("iwf_weightlifting.action_penalties");
  }

  viewMedals() {
    this.actionService.doAction("iwf_weightlifting.action_results");
  }
}

DashboardOrganizer.template = "iwf_weightlifting.DashboardOrganizer";
DashboardOrganizer.components = { KpiCard, ChartRender };

registry.category("actions").add("iwf_weightlifting.dashboard_organizer", DashboardOrganizer);