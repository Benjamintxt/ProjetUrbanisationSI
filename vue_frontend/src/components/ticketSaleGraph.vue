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
        selectedTimeframe: 'daily',
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
        selectedEventTotalSales: 0,
        };
    },
    
    created() {
        this.socket = io('http://127.0.0.1:5000/');

        this.socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });

        this.socket.on('ticket_created', (data) => {
            console.log('Received new created ticket :', data);
            this.scheduleRealTimeUpdate();
            
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
        this.updateChart();
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

        filterSalesDataByTimeframe(groupedSalesData, timeframe) {
            const filteredData = {};

            const currentDate = new Date();
            const startDate = new Date(currentDate);

            // Adjust startDate based on the selected timeframe
            switch (timeframe) {
                case 'day':
                    startDate.setDate(currentDate.getDate() - 7); // Assuming 7 days for daily timeframe
                    break;
                case 'hour':
                    startDate.setHours(currentDate.getHours() - 24);
                    break;
                case 'minute':
                    startDate.setMinutes(currentDate.getMinutes() - 60);
                    break;
                default:
                    break;
            }

            // Filter data based on the selected timeframe
            for (const timestamp in groupedSalesData) {
                const date = new Date(timestamp);
                if (date >= startDate) {
                    if (timeframe === 'hour'){
                        const formattedDate = this.formatDate(date, 'hour');
                        filteredData[formattedDate] = (filteredData[formattedDate] || 0) + groupedSalesData[timestamp];
                        console.log('Filtered Data:', filteredData);
                    }else if (timeframe === 'minute'){
                        const formattedDate = this.formatDate(date, 'minute');
                        filteredData[formattedDate] = (filteredData[formattedDate] || 0) + groupedSalesData[timestamp];
                        console.log('Filtered Data:', filteredData);
                    }
                    else {
                        const formattedDate = this.formatDateForDaily(date);
                        filteredData[formattedDate] = (filteredData[formattedDate] || 0) + groupedSalesData[timestamp];
                        console.log('Filtered Data:', filteredData);
                    }
                    
                }
            }

            return filteredData;
        },

        groupSalesDataByDay(salesData) {
            const grouped = {};

            salesData.forEach((sale) => {
                const date = new Date(sale);

                const key = this.formatDateForDaily(date);

                if (!grouped[key]) {
                    grouped[key] = 0;
                }

                grouped[key] ++;
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
            const grouped = {};

            salesData.forEach((sale) => {
                const date = new Date(sale);

                let key;
                switch (timeframe) {
                    case 'daily':
                        key = this.formatDateForDaily(date);
                        break;
                    case 'hour':
                        key = this.formatDate(date, 'hour');
                        break;
                    case 'minute':
                        key = this.formatDate(date, 'minute');
                        break;
                    default:
                        break;
                }

                if (!grouped[key]) {
                    grouped[key] = 0;
                }

                grouped[key]++;
            });

            return grouped;
        },

        updateChartData() {
            let dataPoints;

            try {
                let groupedSalesData = this.groupSalesDataByTimeframe(this.salesData, this.selectedTimeframe);

                switch (this.selectedTimeframe) {
                    case 'daily':
                        groupedSalesData = this.filterSalesDataByTimeframe(groupedSalesData, 'day');
                        dataPoints = this.getLastNDaysDataPoints(groupedSalesData, 7);
                        break;
                    case 'hour':
                        groupedSalesData = this.filterSalesDataByTimeframe(groupedSalesData, 'hour');
                        dataPoints = this.getLastNHoursDataPoints(groupedSalesData, 24);
                        break;
                    case 'minute':
                        groupedSalesData = this.filterSalesDataByTimeframe(groupedSalesData, 'minute');
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
                        const initialDataResponse = await axios.get(`http://127.0.0.1:5000/event-ticket-sales/${this.selectedEvent}`);
                        this.salesData = initialDataResponse.data.event_ticket_sales;

                        this.socket.send(JSON.stringify({ event_id: this.selectedEvent }));

                        this.updateChartData();
                    } catch (error) {
                        console.error('Error fetching sales data:', error);
                    }
                };

                  
                fetchData();
                
                
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
            
                    //this.updateChart();
                    this.chart.render();
                    setTimeout(this.updateChart, 1000);     

                    this.fetchEventSalesCount();

                // Reset the flag
                this.realTimeUpdatePending = false;
                }
            }, 1000); // Adjust the timeout as needed
            }, 1000), // Adjust the throttle duration as needed



        getXValueFormatString() {
            switch (this.selectedTimeframe) {
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

            // Fetch total sales count for the event
            const total = this.selectedEventTotalSales;
            
            const totalSalesInTimeframe = Object.values(groupedSalesData).reduce((sum, count) => sum + count, 0);
            console.log('Total Sales in Timeframe:', totalSalesInTimeframe);
            // Set initial cumulativeCount to (total - total sales in the selected timeframe)
            cumulativeCount = total - totalSalesInTimeframe;
            console.log('Initial Cumulative Count:', cumulativeCount);

            while (currentDate <= endDate) {
                const key = this.formatDate(currentDate, timeframe);

                const count = groupedSalesData[key] || 0;
                cumulativeCount += count;

                dataPoints.push({
                    x: new Date(currentDate),
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
                case 'daily':
                return this.formatDateForDaily(date);
                case 'hour':
                return this.formatDateForDaily(date) + ' ' + this.pad(date.getHours()) + ':00';
                case 'minute':
                return this.formatDateForDaily(date) + ' ' + this.pad(date.getHours()) + ':' + this.pad(date.getMinutes());
                default:
                return '';
            }
        },

        formatDateForDaily(date) {
            if (!date) {
                return '';
            }

            if (typeof date === 'string') {
                date = new Date(date);
            }

            const options = { year: 'numeric', month: 'numeric', day: 'numeric' };
            return Intl.DateTimeFormat('en-US', options).format(date);
        },

        decrementDate(date, timeframe) {
        const newDate = new Date(date);
        switch (timeframe) {
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
    props: ['events'],
    };
</script>