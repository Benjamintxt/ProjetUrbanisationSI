import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import VueAxios from 'vue-axios';

import CanvasJSChart from '@canvasjs/vue-charts';

const app = createApp(App);

axios.defaults.baseURL = 'http://localhost:5000';

app.use(VueAxios, axios);
app.use(CanvasJSChart);

app.use(router);

app.mount('#app');
