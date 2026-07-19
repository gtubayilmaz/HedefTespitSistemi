/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : HC-SR04 mesafe ölçümü
  ******************************************************************************
  */
/* USER CODE END Header */

#include "main.h"

/* Private variables ---------------------------------------------------------*/

TIM_HandleTypeDef htim4;

/* USER CODE BEGIN PV */

volatile uint32_t echo_rise = 0;
volatile uint32_t echo_fall = 0;
volatile uint32_t echo_pulse_us = 0;

volatile float distance_cm = 0.0f;
volatile uint8_t capture_state = 0;
volatile uint8_t measurement_ready = 0;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM4_Init(void);

/* USER CODE BEGIN PFP */

static void DWT_Delay_Init(void);
static void delay_us(uint32_t microseconds);
static void HCSR04_Trigger(void);

/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

/**
  * @brief DWT mikrosaniye gecikme sayacını başlatır.
  */
static void DWT_Delay_Init(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;

    DWT->CYCCNT = 0;

    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

/**
  * @brief Mikrosaniye cinsinden bloklayıcı gecikme.
  */
static void delay_us(uint32_t microseconds)
{
    uint32_t start_cycle;
    uint32_t required_cycles;

    start_cycle = DWT->CYCCNT;

    required_cycles =
        microseconds * (SystemCoreClock / 1000000U);

    while ((DWT->CYCCNT - start_cycle) < required_cycles)
    {
        /* Bekle */
    }
}

/**
  * @brief HC-SR04 sensörüne 10 us TRIG sinyali gönderir.
  */
static void HCSR04_Trigger(void)
{
    /*
     * Önceki ölçüm tamamlanmadıysa sistemi tekrar
     * yükselen kenar bekleyecek duruma getir.
     */
    if (capture_state != 0)
    {
        capture_state = 0;

        __HAL_TIM_SET_CAPTUREPOLARITY(
            &htim4,
            TIM_CHANNEL_3,
            TIM_INPUTCHANNELPOLARITY_RISING
        );

        __HAL_TIM_SET_COUNTER(&htim4, 0);
    }

    measurement_ready = 0;

    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_9,
        GPIO_PIN_RESET
    );

    delay_us(2);

    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_9,
        GPIO_PIN_SET
    );

    delay_us(10);

    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_9,
        GPIO_PIN_RESET
    );
}

/**
  * @brief TIM4 Input Capture kesme fonksiyonu.
  */
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
    if ((htim->Instance == TIM4) &&
        (htim->Channel == HAL_TIM_ACTIVE_CHANNEL_3))
    {
        /*
         * İlk kesme ECHO sinyalinin yükselen kenarıdır.
         */
        if (capture_state == 0)
        {
            echo_rise = HAL_TIM_ReadCapturedValue(
                htim,
                TIM_CHANNEL_3
            );

            /*
             * Darbe süresini doğrudan okuyabilmek için
             * sayacı yükselen kenarda sıfırla.
             */
            __HAL_TIM_SET_COUNTER(htim, 0);

            capture_state = 1;

            /*
             * Bundan sonra düşen kenarı bekle.
             */
            __HAL_TIM_SET_CAPTUREPOLARITY(
                htim,
                TIM_CHANNEL_3,
                TIM_INPUTCHANNELPOLARITY_FALLING
            );
        }
        else
        {
            /*
             * İkinci kesme ECHO sinyalinin düşen kenarıdır.
             */
            echo_fall = HAL_TIM_ReadCapturedValue(
                htim,
                TIM_CHANNEL_3
            );

            /*
             * Timer 1 MHz çalıştığı için her sayaç değeri
             * 1 mikrosaniyeye karşılık gelir.
             */
            echo_pulse_us = echo_fall;

            /*
             * HC-SR04 yaklaşık mesafe hesabı:
             *
             * Mesafe (cm) = ECHO süresi (us) / 58
             */
            distance_cm =
                (float)echo_pulse_us / 58.0f;

            measurement_ready = 1;
            capture_state = 0;

            /*
             * Sonraki ölçüm için tekrar yükselen kenarı bekle.
             */
            __HAL_TIM_SET_CAPTUREPOLARITY(
                htim,
                TIM_CHANNEL_3,
                TIM_INPUTCHANNELPOLARITY_RISING
            );

            __HAL_TIM_SET_COUNTER(htim, 0);
        }
    }
}

/* USER CODE END 0 */

/**
  * @brief Ana program.
  */
int main(void)
{
    HAL_Init();

    SystemClock_Config();

    MX_GPIO_Init();
    MX_TIM4_Init();

    /* USER CODE BEGIN 2 */

    DWT_Delay_Init();

    __HAL_TIM_SET_COUNTER(&htim4, 0);

    if (HAL_TIM_IC_Start_IT(
            &htim4,
            TIM_CHANNEL_3
        ) != HAL_OK)
    {
        Error_Handler();
    }

    /* USER CODE END 2 */

    while (1)
    {
        /* USER CODE BEGIN WHILE */

        HCSR04_Trigger();

        /*
         * HC-SR04 ölçümleri arasında en az yaklaşık
         * 60 ms bırakılması önerilir.
         */
        HAL_Delay(60);

        /* USER CODE END WHILE */

        /* USER CODE BEGIN 3 */

        /*
         * Ölçülen değerler:
         *
         * distance_cm
         * echo_pulse_us
         *
         * CubeIDE Debug > Live Expressions bölümünden
         * izlenebilir.
         */

        /* USER CODE END 3 */
    }
}

/**
  * @brief Sistem saat ayarı.
  *
  * HSE: 8 MHz
  * SYSCLK: 168 MHz
  * APB1 Timer Clock: 84 MHz
  */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();

    __HAL_PWR_VOLTAGESCALING_CONFIG(
        PWR_REGULATOR_VOLTAGE_SCALE1
    );

    RCC_OscInitStruct.OscillatorType =
        RCC_OSCILLATORTYPE_HSE;

    RCC_OscInitStruct.HSEState =
        RCC_HSE_ON;

    RCC_OscInitStruct.PLL.PLLState =
        RCC_PLL_ON;

    RCC_OscInitStruct.PLL.PLLSource =
        RCC_PLLSOURCE_HSE;

    RCC_OscInitStruct.PLL.PLLM = 8;
    RCC_OscInitStruct.PLL.PLLN = 336;

    RCC_OscInitStruct.PLL.PLLP =
        RCC_PLLP_DIV2;

    RCC_OscInitStruct.PLL.PLLQ = 7;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    RCC_ClkInitStruct.ClockType =
        RCC_CLOCKTYPE_HCLK |
        RCC_CLOCKTYPE_SYSCLK |
        RCC_CLOCKTYPE_PCLK1 |
        RCC_CLOCKTYPE_PCLK2;

    RCC_ClkInitStruct.SYSCLKSource =
        RCC_SYSCLKSOURCE_PLLCLK;

    RCC_ClkInitStruct.AHBCLKDivider =
        RCC_SYSCLK_DIV1;

    RCC_ClkInitStruct.APB1CLKDivider =
        RCC_HCLK_DIV4;

    RCC_ClkInitStruct.APB2CLKDivider =
        RCC_HCLK_DIV2;

    if (HAL_RCC_ClockConfig(
            &RCC_ClkInitStruct,
            FLASH_LATENCY_5
        ) != HAL_OK)
    {
        Error_Handler();
    }
}

/**
  * @brief TIM4 ayarları.
  *
  * TIM4 Clock: 84 MHz
  * Prescaler: 83
  * Sayaç frekansı: 1 MHz
  * Sayaç çözünürlüğü: 1 us
  */
static void MX_TIM4_Init(void)
{
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    TIM_IC_InitTypeDef sConfigIC = {0};

    __HAL_RCC_TIM4_CLK_ENABLE();

    htim4.Instance = TIM4;

    htim4.Init.Prescaler = 83;

    htim4.Init.CounterMode =
        TIM_COUNTERMODE_UP;

    htim4.Init.Period = 65535;

    htim4.Init.ClockDivision =
        TIM_CLOCKDIVISION_DIV1;

    htim4.Init.AutoReloadPreload =
        TIM_AUTORELOAD_PRELOAD_DISABLE;

    if (HAL_TIM_Base_Init(&htim4) != HAL_OK)
    {
        Error_Handler();
    }

    sClockSourceConfig.ClockSource =
        TIM_CLOCKSOURCE_INTERNAL;

    if (HAL_TIM_ConfigClockSource(
            &htim4,
            &sClockSourceConfig
        ) != HAL_OK)
    {
        Error_Handler();
    }

    if (HAL_TIM_IC_Init(&htim4) != HAL_OK)
    {
        Error_Handler();
    }

    sMasterConfig.MasterOutputTrigger =
        TIM_TRGO_RESET;

    sMasterConfig.MasterSlaveMode =
        TIM_MASTERSLAVEMODE_DISABLE;

    if (HAL_TIMEx_MasterConfigSynchronization(
            &htim4,
            &sMasterConfig
        ) != HAL_OK)
    {
        Error_Handler();
    }

    sConfigIC.ICPolarity =
        TIM_INPUTCHANNELPOLARITY_RISING;

    sConfigIC.ICSelection =
        TIM_ICSELECTION_DIRECTTI;

    sConfigIC.ICPrescaler =
        TIM_ICPSC_DIV1;

    sConfigIC.ICFilter = 0;

    if (HAL_TIM_IC_ConfigChannel(
            &htim4,
            &sConfigIC,
            TIM_CHANNEL_3
        ) != HAL_OK)
    {
        Error_Handler();
    }

    HAL_NVIC_SetPriority(
        TIM4_IRQn,
        0,
        0
    );

    HAL_NVIC_EnableIRQ(TIM4_IRQn);
}

/**
  * @brief GPIO ayarları.
  */
static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOB_CLK_ENABLE();

    /*
     * PB9 başlangıçta LOW.
     */
    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_9,
        GPIO_PIN_RESET
    );

    /*
     * PB9: HC-SR04 TRIG çıkışı.
     */
    GPIO_InitStruct.Pin =
        GPIO_PIN_9;

    GPIO_InitStruct.Mode =
        GPIO_MODE_OUTPUT_PP;

    GPIO_InitStruct.Pull =
        GPIO_NOPULL;

    GPIO_InitStruct.Speed =
        GPIO_SPEED_FREQ_LOW;

    HAL_GPIO_Init(
        GPIOB,
        &GPIO_InitStruct
    );

    /*
     * PB8: TIM4 Channel 3 Input Capture.
     */
    GPIO_InitStruct.Pin =
        GPIO_PIN_8;

    GPIO_InitStruct.Mode =
        GPIO_MODE_AF_PP;

    GPIO_InitStruct.Pull =
        GPIO_NOPULL;

    GPIO_InitStruct.Speed =
        GPIO_SPEED_FREQ_LOW;

    GPIO_InitStruct.Alternate =
        GPIO_AF2_TIM4;

    HAL_GPIO_Init(
        GPIOB,
        &GPIO_InitStruct
    );
}

/**
  * @brief Hata durumunda programı durdurur.
  */
void Error_Handler(void)
{
    __disable_irq();

    while (1)
    {
    }
}

#ifdef USE_FULL_ASSERT

void assert_failed(
    uint8_t *file,
    uint32_t line
)
{
    /*
     * Gerekirse hata dosyası ve satır numarası
     * burada incelenebilir.
     */
}

#endif
