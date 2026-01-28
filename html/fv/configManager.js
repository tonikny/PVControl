class ConfigManager {
  constructor() {
    if (ConfigManager.instance) {
      return ConfigManager.instance;
    }

    this.config = {};
    this.configUrl = '';
    this.lastModified = null;
    this.isConfigUpdated = false;
    ConfigManager.instance = this;
  }

  async loadConfig(file) {
    this.configUrl = `configuraciones/${file}`;
    console.log('Loading config from:', this.configUrl);
    try {
      const response = await fetch(this.configUrl, {
        // method: 'HEAD',
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }

      const configResponse = await fetch(this.configUrl);
      if (!configResponse.ok) {
        throw new Error(
          `Network response was not ok: ${configResponse.statusText}`
        );
      }

      this.config = await configResponse.json();
      this.isConfigUpdated = true;

      console.log('Configuration updated');
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  }

  getConfig() {
    return this.config;
  }
}

const instance = new ConfigManager();
export default instance;
