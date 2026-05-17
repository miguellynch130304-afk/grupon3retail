# ============================================================================
# Módulo de Visualización Avanzada con R/ggplot2
# Genera gráficos académicos profesionales complementarios en R
# ============================================================================

# Cargar librerías necesarias
library(tidyverse)  # ggplot2, dplyr, tidyr
library(ggplot2)
library(dplyr)
library(readr)
library(scales)
library(gridExtra)
library(RColorBrewer)

# Configurar tema de ggplot2 para publicaciones académicas
theme_academic <- function() {
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold", hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5, color = "gray40"),
    axis.title = element_text(size = 11, face = "bold"),
    axis.text = element_text(size = 10),
    legend.position = "right",
    legend.title = element_text(size = 10, face = "bold"),
    legend.text = element_text(size = 9),
    panel.grid.major = element_line(color = "gray90"),
    panel.grid.minor = element_blank(),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  )
}

# Directorios de datos
data_dir <- "./data/processed/merged"
analytics_dir <- "./data/processed/analytics"
outputs_dir <- "./outputs/visualizations"

# Crear directorio de salida si no existe
dir.create(outputs_dir, showWarnings = FALSE, recursive = TRUE)

# ============================================================================
# 1. ANÁLISIS GEOGRÁFICO - Mapa de concentración de pedidos
# ============================================================================
generate_geographic_analysis <- function() {
  tryCatch({
    cat("Generando análisis geográfico...\n")
    
    # Leer datos consolidados
    if (file.exists(file.path(data_dir, "orders_with_details.parquet"))) {
      df <- arrow::read_parquet(file.path(data_dir, "orders_with_details.parquet"))
    } else if (file.exists(file.path(data_dir, "orders_with_details.csv"))) {
      df <- read_csv(file.path(data_dir, "orders_with_details.csv"), show_col_types = FALSE)
    } else {
      warning("No se encontraron datos consolidados")
      return(NULL)
    }
    
    # Agrupar por estado
    state_analysis <- df %>%
      group_by(customer_state) %>%
      summarise(
        num_orders = n(),
        total_revenue = sum(total_payment, na.rm = TRUE),
        avg_rating = mean(avg_review_score, na.rm = TRUE),
        .groups = 'drop'
      ) %>%
      arrange(desc(num_orders)) %>%
      head(15)  # Top 15 estados
    
    # Gráfico 1: Top Estados por Número de Pedidos
    p1 <- ggplot(state_analysis, aes(x = reorder(customer_state, num_orders), 
                                      y = num_orders, 
                                      fill = num_orders)) +
      geom_bar(stat = "identity", color = "black", alpha = 0.85) +
      coord_flip() +
      scale_fill_gradient(low = "#3498db", high = "#e74c3c", name = "Pedidos") +
      labs(
        title = "Distribución Geográfica de Pedidos",
        subtitle = "Top 15 Estados - Sistema de E-Commerce Olist Brasil",
        x = "Estado (UF)",
        y = "Número de Pedidos"
      ) +
      theme_academic() +
      theme(legend.position = "right")
    
    # Gráfico 2: Ingresos vs Satisfacción por Estado
    p2 <- ggplot(state_analysis, aes(x = total_revenue, 
                                      y = avg_rating, 
                                      size = num_orders,
                                      color = customer_state)) +
      geom_point(alpha = 0.6) +
      scale_size_continuous(name = "Pedidos", range = c(3, 15)) +
      scale_color_manual(values = colorRampPalette(brewer.pal(9, "Set1"))(15)) +
      labs(
        title = "Relación: Ingresos vs Satisfacción del Cliente",
        subtitle = "Tamaño de burbujas = Volumen de pedidos",
        x = "Ingresos Totales (BRL)",
        y = "Calificación Promedio (1-5)"
      ) +
      theme_academic() +
      theme(legend.position = "none")
    
    # Guardar gráficos combinados
    combined <- gridExtra::grid.arrange(p1, p2, nrow = 2)
    ggsave(
      file.path(outputs_dir, "06_geographic_analysis.png"),
      combined,
      width = 14,
      height = 11,
      dpi = 300,
      units = "in"
    )
    
    cat("Gráfico geográfico guardado: 06_geographic_analysis.png\n")
    return(TRUE)
    
  }, error = function(e) {
    cat("Error en análisis geográfico:", conditionMessage(e), "\n")
    return(FALSE)
  })
}

# ============================================================================
# 2. ANÁLISIS TEMPORAL - Tendencias de ventas
# ============================================================================
generate_temporal_analysis <- function() {
  tryCatch({
    cat("Generando análisis temporal...\n")
    
    # Leer datos
    if (file.exists(file.path(data_dir, "orders_with_details.parquet"))) {
      df <- arrow::read_parquet(file.path(data_dir, "orders_with_details.parquet"))
    } else if (file.exists(file.path(data_dir, "orders_with_details.csv"))) {
      df <- read_csv(file.path(data_dir, "orders_with_details.csv"), show_col_types = FALSE)
    } else {
      warning("No se encontraron datos consolidados")
      return(NULL)
    }
    
    # Preparar datos temporales
    df <- df %>%
      mutate(
        order_date = as.Date(order_purchase_timestamp),
        year_month = format(order_date, "%Y-%m")
      )
    
    temporal_data <- df %>%
      group_by(year_month) %>%
      summarise(
        total_orders = n(),
        total_revenue = sum(total_payment, na.rm = TRUE),
        avg_order_value = mean(total_payment, na.rm = TRUE),
        .groups = 'drop'
      ) %>%
      mutate(year_month = as.Date(paste0(year_month, "-01")))
    
    # Gráfico 3: Tendencia de Pedidos y Ingresos
    p3 <- ggplot(temporal_data, aes(x = year_month)) +
      geom_line(aes(y = total_orders), color = "#3498db", size = 1.2) +
      geom_point(aes(y = total_orders), color = "#3498db", size = 3) +
      scale_y_continuous(name = "Número de Pedidos", sec.axis = sec_axis(~. * mean(temporal_data$total_revenue) / mean(temporal_data$total_orders), name = "Ingresos (BRL)")) +
      labs(
        title = "Evolución Temporal de Pedidos e Ingresos",
        subtitle = "Tendencia mensual del período de análisis",
        x = "Mes"
      ) +
      theme_academic()
    
    # Gráfico 4: Valor Promedio de Pedido por Mes
    p4 <- ggplot(temporal_data, aes(x = year_month, y = avg_order_value, fill = avg_order_value)) +
      geom_bar(stat = "identity", color = "black", alpha = 0.8) +
      scale_fill_gradient(low = "#95a5a6", high = "#f39c12", name = "APV (BRL)") +
      labs(
        title = "Valor Promedio de Pedido (APV) Mensual",
        subtitle = "Análisis de ticket promedio",
        x = "Mes",
        y = "APV (BRL)"
      ) +
      scale_y_continuous(labels = dollar_format(prefix = "R$ ", suffix = "", big.mark = ",", decimal.mark = ".")) +
      theme_academic()
    
    # Guardar gráficos combinados
    combined <- gridExtra::grid.arrange(p3, p4, nrow = 2)
    ggsave(
      file.path(outputs_dir, "07_temporal_analysis.png"),
      combined,
      width = 14,
      height = 11,
      dpi = 300,
      units = "in"
    )
    
    cat("Gráfico temporal guardado: 07_temporal_analysis.png\n")
    return(TRUE)
    
  }, error = function(e) {
    cat("Error en análisis temporal:", conditionMessage(e), "\n")
    return(FALSE)
  })
}

# ============================================================================
# 3. ANÁLISIS DE PAGO - Métodos de pago y cumplimiento
# ============================================================================
generate_category_analysis <- function() {
  tryCatch({
    cat("📊 Generando análisis de métodos de pago...\n")
    
    # Leer datos
    if (file.exists(file.path(data_dir, "orders_with_details.parquet"))) {
      df <- arrow::read_parquet(file.path(data_dir, "orders_with_details.parquet"))
    } else if (file.exists(file.path(data_dir, "orders_with_details.csv"))) {
      df <- read_csv(file.path(data_dir, "orders_with_details.csv"), show_col_types = FALSE)
    } else {
      warning("No se encontraron datos consolidados")
      return(NULL)
    }
    
    # Análisis de estado de pedidos
    status_analysis <- df %>%
      group_by(order_status) %>%
      summarise(
        num_orders = n(),
        total_revenue = sum(total_payment, na.rm = TRUE),
        avg_rating = mean(avg_review_score, na.rm = TRUE),
        .groups = 'drop'
      ) %>%
      arrange(desc(total_revenue))
    
    # Gráfico 5: Ingresos por Estado de Pedido
    p5 <- ggplot(status_analysis, aes(x = reorder(order_status, total_revenue), 
                                       y = total_revenue,
                                       fill = avg_rating)) +
      geom_bar(stat = "identity", color = "black", alpha = 0.85) +
      coord_flip() +
      scale_fill_gradient(low = "#e74c3c", high = "#2ecc71", 
                         name = "Rating Promedio",
                         limits = c(1, 5)) +
      labs(
        title = "Análisis de Ingresos por Estado de Pedido",
        subtitle = "Colorizado por calificación promedio (1-5)",
        x = "Estado del Pedido",
        y = "Ingresos (BRL)"
      ) +
      scale_y_continuous(labels = dollar_format(prefix = "R$ ", suffix = "M", scale = 1/1000000, big.mark = ",", decimal.mark = ".")) +
      theme_academic()
    
    # Análisis de tiempo de entrega
    delivery_analysis <- df %>%
      filter(order_status == "delivered") %>%
      mutate(
        delivery_category = cut(
          delivery_time_days,
          breaks = c(0, 5, 10, 15, 30, Inf),
          labels = c("1-5 días", "6-10 días", "11-15 días", "16-30 días", ">30 días")
        )
      ) %>%
      group_by(delivery_category) %>%
      summarise(
        num_orders = n(),
        avg_rating = mean(avg_review_score, na.rm = TRUE),
        .groups = 'drop'
      )
    
    # Gráfico 6: Matriz de Volumen vs Performance
    p6 <- ggplot(delivery_analysis, aes(x = delivery_category, 
                                         y = avg_rating,
                                         fill = num_orders)) +
      geom_bar(stat = "identity", color = "black", alpha = 0.8) +
      scale_fill_gradient(low = "#3498db", high = "#e74c3c", name = "# Órdenes") +
      labs(
        title = "Performance de Entregas: Tiempo vs Satisfacción",
        subtitle = "Análisis de categorías de tiempo de entrega",
        x = "Categoría de Tiempo de Entrega",
        y = "Calificación Promedio (1-5)"
      ) +
      theme_academic() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
    
    # Guardar gráficos combinados
    combined <- gridExtra::grid.arrange(p5, p6, nrow = 2)
    ggsave(
      file.path(outputs_dir, "08_payment_delivery_analysis.png"),
      combined,
      width = 14,
      height = 11,
      dpi = 300,
      units = "in"
    )
    
    cat("Gráfico de pago/entrega guardado: 08_payment_delivery_analysis.png\n")
    return(TRUE)
    
  }, error = function(e) {
    cat("Error en análisis de pago:", conditionMessage(e), "\n")
    return(FALSE)
  })
}

# ============================================================================
# 4. MATRIZ DE CORRELACIÓN - Relaciones clave
# ============================================================================
generate_correlation_analysis <- function() {
  tryCatch({
    cat("📊 Generando matriz de correlación...\n")
    
    # Leer datos
    if (file.exists(file.path(data_dir, "orders_with_details.parquet"))) {
      df <- arrow::read_parquet(file.path(data_dir, "orders_with_details.parquet"))
    } else if (file.exists(file.path(data_dir, "orders_with_details.csv"))) {
      df <- read_csv(file.path(data_dir, "orders_with_details.csv"), show_col_types = FALSE)
    } else {
      warning("No se encontraron datos consolidados")
      return(NULL)
    }
    
    # Seleccionar variables numéricas clave
    numeric_cols <- c("total_payment", "avg_review_score", "delivery_time_days", "avg_price", "avg_freight")
    numeric_cols <- numeric_cols[numeric_cols %in% names(df)]
    
    if (length(numeric_cols) > 1) {
      # Calcular correlación
      corr_matrix <- cor(df[, numeric_cols], use = "complete.obs")
      
      # Preparar datos para heatmap
      corr_df <- as.data.frame(as.table(corr_matrix))
      names(corr_df) <- c("Var1", "Var2", "Correlation")
      
      # Renombrar columnas para mejor visualización
      corr_df$Var1 <- recode(corr_df$Var1,
        "total_payment" = "Ingresos",
        "avg_review_score" = "Calificación",
        "delivery_time_days" = "Tiempo Entrega",
        "avg_price" = "Precio Promedio",
        "avg_freight" = "Flete Promedio"
      )
      corr_df$Var2 <- recode(corr_df$Var2,
        "total_payment" = "Ingresos",
        "avg_review_score" = "Calificación",
        "delivery_time_days" = "Tiempo Entrega",
        "avg_price" = "Precio Promedio",
        "avg_freight" = "Flete Promedio"
      )
      
      # Gráfico 7: Heatmap de Correlación
      p7 <- ggplot(corr_df, aes(x = Var1, y = Var2, fill = Correlation)) +
        geom_tile(color = "white", size = 1) +
        geom_text(aes(label = round(Correlation, 2)), size = 4, fontface = "bold") +
        scale_fill_gradient2(low = "#3498db", mid = "white", high = "#e74c3c", 
                            name = "Correlación",
                            limits = c(-1, 1)) +
        labs(
          title = "Matriz de Correlación - Variables Clave",
          subtitle = "Análisis de relaciones multivariadas",
          x = "",
          y = ""
        ) +
        theme_academic() +
        theme(axis.text.x = element_text(angle = 45, hjust = 1),
              axis.text.y = element_text(angle = 0))
      
      ggsave(
        file.path(outputs_dir, "09_correlation_matrix.png"),
        p7,
        width = 10,
        height = 8,
        dpi = 300,
        units = "in"
      )
      
      cat("Matriz de correlación guardada: 09_correlation_matrix.png\n")
      return(TRUE)
    } else {
      cat("Insuficientes variables numéricas para análisis de correlación\n")
      return(FALSE)
    }
    
  }, error = function(e) {
    cat("Error en análisis de correlación:", conditionMessage(e), "\n")
    return(FALSE)
  })
}

# ============================================================================
# FUNCIÓN PRINCIPAL - Ejecutar todos los análisis
# ============================================================================
main <- function() {
  cat("\n")
  cat("╔══════════════════════════════════════════════════════════════╗\n")
  cat("║     GENERADOR DE VISUALIZACIONES AVANZADAS - R/ggplot2      ║\n")
  cat("║           Análisis Estadístico Complementario                ║\n")
  cat("╚══════════════════════════════════════════════════════════════╝\n\n")
  
  results <- list(
    geographic = generate_geographic_analysis(),
    temporal = generate_temporal_analysis(),
    payment = generate_category_analysis(),
    correlation = generate_correlation_analysis()
  )
  
  cat("\n")
  cat("╔══════════════════════════════════════════════════════════════╗\n")
  cat("║                    RESUMEN DE GENERACIÓN                     ║\n")
  cat("╠══════════════════════════════════════════════════════════════╣\n")
  cat("║ Geográfico:       ", if(results$geographic) "Completado" else "Error", "     ║\n")
  cat("║ Temporal:         ", if(results$temporal) "Completado" else "Error", "     ║\n")
  cat("║ Pago/Entrega:     ", if(results$payment) "Completado" else "Error", "     ║\n")
  cat("Visualizaciones guardadas en: ./outputs/visualizations/\n")
  cat("Resolución: 300 DPI (calidad académica para publicación)\n\n")
}

# Ejecutar
if (!require("arrow")) {
  tryCatch({
    install.packages("arrow", repos = "http://cran.r-project.org")
  }, error = function(e) {
    cat("Note: arrow no disponible, usando CSV como alternativa\n")
  })
}

main()
