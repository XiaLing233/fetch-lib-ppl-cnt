<template>
  <a-layout>
    <a-layout-header>
        <img src="./assets/logo-final.png" class="logo" alt="Logo" />
        <div style="float:inline-end; padding-top: 8px"><a href="https://github.com/XiaLing233/fetch-lib-ppl-cnt" target="_blank"><GithubFilled style="color:#fff; font-size: 40px;"/></a></div>
    </a-layout-header>
    <a-layout style="min-height: calc(100vh - 195px);">
      <a-layout-sider width="200" style="background: #fff">
        <a-menu
          :default-selected-keys="['/']"
          :selected-keys="[$route.path]"
          mode="inline"
          theme="light"
          @select="menuSelect"
        >
        <a-menu-item key="/show">
          <LineChartOutlined style="margin-right: 8px;" />数据显示
        </a-menu-item>
        <a-menu-item key="/about">
          <InfoCircleOutlined style="margin-right:8px" />本站说明
        </a-menu-item>
        <a-menu-item key="/log">
          <BookOutlined style="margin-right:8px" />更新日志
        </a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout>
        <a-layout-content>
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
    <a-layout-footer class="footer">
          <p>鸣谢：同济大学</p>
          <p>{{ new Date().getFullYear() }} — <strong>夏凌</strong></p>
    </a-layout-footer>
  </a-layout>
  
</template>

<script>
  import { HomeOutlined, LineChartOutlined, GithubFilled, InfoCircleOutlined, BookOutlined} from '@ant-design/icons-vue';
 

  export default {
    components: {
      HomeOutlined,
      LineChartOutlined,
      GithubFilled,
      InfoCircleOutlined,
      BookOutlined
    },

    data() {
      return {
        current: this.$route.path,
      };
    },
    methods: {
      menuSelect({ key }) {
        this.$router.push(key);
      },
    },
  };

</script>

<style scoped>
.logo {
  height: 64px;
  margin-top: 4px;
  margin-bottom: 4px;
}

.footer {
  text-align: center;
}

.footer p {
  margin: 2px 2px 0 0;
}
</style>