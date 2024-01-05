<template>
  <div>
    <h1>Ventes événements</h1>

    <div v-if="selectedEventInfo">
      <h2>{{ selectedEventInfo.eventName }}</h2>
      <p>Total Sales: {{ selectedEventInfo.totalSales }}</p>
    </div>

    <TicketSaleGraph
      :events="events"
      :fetch-event-sales-count="fetchEventSalesCount"
    />

  </div>
</template>

<script>
import io from 'socket.io-client';
import TicketSaleGraph from './components/ticketSaleGraph.vue';

const socket = io('http://127.0.0.1:5000/');

export default {
  components: {
    TicketSaleGraph,
  },
  data() {
    return {
      events: [],
      eventSalesCount: null,
      allEvents: [],
      selectedEvent: null,
      selectedEventInfo: null,
    };
  },
  created() {
    this.fetchEvents();
  },
  beforeUnmount() {
    // Disconnect the WebSocket when the component is destroyed
    socket.disconnect();
  },
  methods: {
    async fetchEvents() {
      try {
        const response = await this.axios.get('http://127.0.0.1:5000/events');
        console.log('Response:', response);
        if (response && response.data) {
          console.log('Events:', response.data.events);
          this.events = response.data.events;
        } else {
          console.error('Invalid response structure:', response);
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    },
    async fetchEventSalesCount(eventId) {
      try {
        const response = await this.axios.get(`http://127.0.0.1:5000/event-sales-count/${eventId}`);
        console.log('Event Sales Count Response:', response);
        if (response && response.data) {
          this.selectedEventInfo = {
            eventName: response.data.eventName,
            totalSales: response.data.totalSales,
          };
        } else {
          console.error('Invalid event sales count response structure:', response);
        }
      } catch (error) {
        console.error('Error fetching event sales count:', error);
      }
    },
    async fetchAllEvents() {
      try {
        const response = await this.axios.get('http://127.0.0.1:5000/events');
        console.log('All Events Response:', response);
        if (response && response.data) {
          this.allEvents = response.data.events;
        } else {
          console.error('Invalid all events response structure:', response);
        }
      } catch (error) {
        console.error('Error fetching all events:', error);
      }
    },
    handleSelectedEventChange(eventId) {
      this.selectedEvent = eventId;
      this.fetchEventSalesCount(eventId);
    },
  },
};
</script>