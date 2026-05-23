import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";
import { useSessionStore } from "./stores/session";
import "./styles/index.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia).use(router).use(ElementPlus);
useSessionStore().restore();
app.mount("#app");
