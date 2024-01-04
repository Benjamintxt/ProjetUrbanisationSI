<template>
    <div>
      <div>
        <h2>Total ventes : {{ selectedEventTotalSales }}</h2>
        <label for="eventSelector">Select Event: </label>
        <select id="eventSelector" v-model="selectedEvent" @change="updateChart">
          <option v-for="event in events" :key="event.eventId" :value="event.eventId">{{ event.eventName }}</option>
        </select>
      </div>
      <div>
        <label for="timeframeSelector">Select Timeframe: </label>
        <select id="timeframeSelector" v-model="selectedTimeframe" @change="updateChart">
          <option value="weekly">Weekly</option>
          <option value="daily">Daily</option>
          <option value="hour">Hourly</option>
          <option value="minute">Minute</option>
        </select>
      </div>
      <CanvasJSChart :options="options" :style="styleOptions" @chart-ref="chartInstance" />
    </div>
  </template>
  
  <script>
    import axios from 'axios';
    import io from 'socket.io-client';
    import { throttle } from 'lodash';

    export default {
    data() {
        return {
        selectedEvent: null,
        selectedTimeframe: 'weekly',
        options: {
            theme: 'light2',
            animationEnabled: true,
            animationDuration: 3000,
            title: {
            text: 'Ventes de billets',
            },
            axisY: {
            title: 'Nombre de billets vendus',
            },
            data: [],
        },
        styleOptions: {
            width: '100%',
            height: '360px',
        },
        salesData: [],
        chart: null,
        realTimeUpdatePending: false,
        selectedEventTotalSales: 0,
        };
    },
    created() {
        this.socket = io('http://127.0.0.1:5000/');

        this.socket.on('webhook_events', (data) => {
            console.log('Received event:', data);
            if (this.updateChartRealTime) {
                this.updateChartRealTime();
            }
        });
        this.fetchEventSalesCount();
    },
    beforeUnmount() {
        // Disconnect the WebSocket when the component is destroyed
        if (this.socket){
            this.socket.disconnect();
        }
    },
    computed: {
        filteredSalesData() {
        const filtered = this.salesData.filter((sale) => sale.eventId === this.selectedEvent);
        return this.groupSalesDataByTimeframe(filtered, this.selectedTimeframe);
        },
    },
    watch: {
        selectedEvent: 'fetchEventSalesCount', 
        selectedTimeframe: 'updateChart',
    },
    methods: {

        chartInstance(chart) {
        this.chart = chart;
        },

        async fetchEventSalesCount() {
            try {
                // Fetch the total sales count for the selected event
                const response = await axios.get(`http://127.0.0.1:5000/event-sales-count/${this.selectedEvent}`);
                console.log('Selected Event Total Sales:', response.data.event_sales_count);

                // Access the event sales count from the response data
                this.selectedEventTotalSales = response.data.event_sales_count;
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        getFormattedDate(date) {
        const options = { year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' };
        return new Intl.DateTimeFormat('en-US', options).format(date);
        },

        getWeekStartDate(date) {
        const weekStartDate = new Date(date);
        weekStartDate.setDate(date.getDate() - date.getDay());
        return this.formatDate(weekStartDate);
        },

        groupSalesDataByWeek(salesData) {
            const grouped = {};

            salesData.forEach((sale) => {
                const key = this.getWeekStartDate(new Date(sale.timestamp));
                if (!grouped[key]) {
                grouped[key] = 0;
                }
                grouped[key]++;
            });

            return grouped;
        },

        groupSalesDataByDay(salesData) {
            const grouped = {};

            salesData.forEach((sale) => {
                const key = this.formatDate(new Date(sale.timestamp), 'daily');
                if (!grouped[key]) {
                grouped[key] = 0;
                }
                grouped[key]++;
            });

            return grouped;
        },


        groupSalesDataByHour(salesData) {
            const grouped = {};

            salesData.forEach((sale) => {
                const key = this.formatDate(new Date(sale), 'hour');
                if (!grouped[key]) {
                grouped[key] = 0;
                }
                grouped[key]++;
            });

            return grouped;
        },

        groupSalesDataByMinute(salesData) {
            const grouped = {};

            salesData.forEach((sale) => {
                const key = this.formatDate(new Date(sale), 'minute');
                if (!grouped[key]) {
                grouped[key] = 0;
                }
                grouped[key]++;
            });

            return grouped;
        },

        groupSalesDataByTimeframe(salesData, timeframe) {
        switch (timeframe) {
            case 'weekly':
            return this.groupSalesDataByWeek(salesData);
            case 'daily':
            return this.groupSalesDataByDay(salesData);
            case 'hour':
            return this.groupSalesDataByHour(salesData);
            case 'minute':
            return this.groupSalesDataByMinute(salesData);
            default:
            return {};
        }
        },

        updateChartData() {
        let dataPoints;

        try {
            let groupedSalesData = this.groupSalesDataByTimeframe(this.salesData, this.selectedTimeframe);

            console.log('Grouped Sales Data:', groupedSalesData);

            switch (this.selectedTimeframe) {
            case 'weekly':
                dataPoints = this.getLastNWeeksDataPoints(groupedSalesData, 6);
                break;
            case 'daily':
                dataPoints = this.getLastNDaysDataPoints(groupedSalesData, 14);
                break;
            case 'hour':
                dataPoints = this.getLastNHoursDataPoints(groupedSalesData, 24);
                break;
            case 'minute':
                dataPoints = this.getLastNMinutesDataPoints(groupedSalesData, 60);
                break;
            default:
                dataPoints = [];
            }

            console.log('Data Points:', dataPoints);
        } catch (error) {
            console.error('Error processing sales data:', error);
            return;
        }

        this.options.data = [
            {
            type: 'line',
            xValueFormatString: this.getXValueFormatString(),
            yValueFormatString: '0,0',
            markerSize: 0,
            dataPoints,
            },
        ];

        console.log('Updated Chart Data:', this.options.data);

        if (this.chart) {
            this.chart.render();
        } else {
            console.error('Chart instance not found.');
        }
        },

        updateChart() {
        if (!this.selectedEvent) return;

            const fetchData = async () => {
                try {
                const response = await axios.get(`http://127.0.0.1:5000/event-ticket-sales/${this.selectedEvent}`);
                console.log('Sales Data Response:', response);
                if (response && response.data) {
                    this.salesData = response.data.event_ticket_sales;
                    console.log('Updated sales data:', this.salesData);
                    this.updateChartData();
                }
                } catch (error) {
                console.error('Error fetching sales data:', error);
                }
            };
            
            fetchData();

            if (this.updateChartRealTime) {
                this.updateChartRealTime();
            }

        },

        pad(num) {
        return num.toString().padStart(2, '0');
        },
        
        scheduleRealTimeUpdate: throttle(function () {
            // Set a flag to indicate a real-time update is pending
            this.realTimeUpdatePending = true;

            // Use a timeout to allow some time for additional events to be received
            setTimeout(() => {
                // Check if a real-time update is pending
                if (this.realTimeUpdatePending) {
                // Perform the real-time update
                this.updateChartRealTime();

                // Reset the flag
                this.realTimeUpdatePending = false;
                }
            }, 1000); // Adjust the timeout as needed
            }, 2000), // Adjust the throttle duration as needed



        getXValueFormatString() {
        switch (this.selectedTimeframe) {
            case 'weekly':
            return 'MMM DD, YYYY';
            case 'daily':
            return 'MMM DD, YYYY';
            case 'hour':
            return 'MMM DD, YYYY HH:00';
            case 'minute':
            return 'MMM DD, YYYY HH:mm';
            default:
            return 'MMM DD, YYYY';
        }
        },

        getLastNWeeksDataPoints(groupedSalesData, n) {
        const endOfWeek = new Date();
        const startOfWeek = new Date(endOfWeek);
        startOfWeek.setDate(endOfWeek.getDate() - n * 7);

        return this.generateDataPoints(startOfWeek, endOfWeek, 'weekly', groupedSalesData);
        },

        getLastNDaysDataPoints(groupedSalesData, n) {
        const endOfDay = new Date();
        const startOfDay = new Date(endOfDay);
        startOfDay.setDate(endOfDay.getDate() - n);

        return this.generateDataPoints(startOfDay, endOfDay, 'daily', groupedSalesData);
        },

        getLastNHoursDataPoints(groupedSalesData, n) {
        const endOfHour = new Date();
        const startOfHour = new Date(endOfHour);
        startOfHour.setHours(endOfHour.getHours() - n);

        return this.generateDataPoints(startOfHour, endOfHour, 'hour', groupedSalesData);
        },

        getLastNMinutesDataPoints(groupedSalesData, n) {
        const endOfMinute = new Date();
        const startOfMinute = new Date(endOfMinute);
        startOfMinute.setMinutes(endOfMinute.getMinutes() - n);

        return this.generateDataPoints(startOfMinute, endOfMinute, 'minute', groupedSalesData);
        },

        generateDataPoints(startDate, endDate, timeframe, groupedSalesData) {
            const dataPoints = [];
            let currentDate = new Date(startDate); // Start from the end date
            let cumulativeCount = 0;

            while (currentDate <= endDate) {
                const key = this.formatDate(currentDate, timeframe);
                
                const count = groupedSalesData[key] || 0;
                cumulativeCount += count;

                dataPoints.push({
                    x: currentDate,
                    y: cumulativeCount,
                });

                currentDate = this.decrementDate(currentDate, timeframe);
            }

            return dataPoints.reverse(); // Reverse the order to display in ascending order
        },


        formatDate(date, timeframe) {
        if (!date) {
            return '';
        }

        switch (timeframe) {
            case 'weekly':
            return this.getWeekStartDate(date);
            case 'daily':
            return this.formatDate(date);
            case 'hour':
            return this.formatDate(date) + ' ' + this.pad(date.getHours()) + ':00';
            case 'minute':
            return this.formatDate(date) + ' ' + this.pad(date.getHours()) + ':' + this.pad(date.getMinutes());
            default:
            return '';
        }
        },

        decrementDate(date, timeframe) {
        const newDate = new Date(date);
        switch (timeframe) {
            case 'weekly':
            newDate.setDate(date.getDate() + 7);
            break;
            case 'daily':
            newDate.setDate(date.getDate() + 1);
            break;
            case 'hour':
            newDate.setHours(date.getHours() + 1);
            break;
            case 'minute':
            newDate.setMinutes(date.getMinutes() + 1);
            break;
            default:
            break;
        }
        return newDate;
        },
    },
    props: ['events', 'updateChartRealTime'],
    };
</script>