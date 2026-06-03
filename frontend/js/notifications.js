/**
 * Notification System
 * Menampilkan alert/notifikasi kepada user
 */

class NotificationManager {
  constructor() {
    this.container = document.getElementById('notificationContainer');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'notificationContainer';
      this.container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
      `;
      document.body.appendChild(this.container);
    }
  }

  show(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
      background: ${this.getBackgroundColor(type)};
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      margin-bottom: 10px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.2);
      animation: slideInRight 0.3s ease-out;
      min-height: 50px;
      display: flex;
      align-items: center;
      font-weight: 500;
    `;
    notification.textContent = message;

    this.container.appendChild(notification);

    if (duration > 0) {
      setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
      }, duration);
    }
  }

  getBackgroundColor(type) {
    const colors = {
      success: '#4caf50',
      error: '#f44336',
      warning: '#ff9800',
      info: '#2196f3'
    };
    return colors[type] || colors.info;
  }

  success(message, duration = 3000) {
    this.show(message, 'success', duration);
  }

  error(message, duration = 5000) {
    this.show(message, 'error', duration);
  }

  warning(message, duration = 3000) {
    this.show(message, 'warning', duration);
  }

  info(message, duration = 3000) {
    this.show(message, 'info', duration);
  }
}

const notify = new NotificationManager();
