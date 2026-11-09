package pe.edu.pe.PharmaBackend.config;

import java.io.IOException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class RequestIdFilterTest {
    private final RequestIdFilter filter = new RequestIdFilter();

    @AfterEach
    void limpiar() {
        MDC.remove(RequestIdFilter.CLAVE_MDC);
    }

    @Test
    void comparteElIdEntreLaCabeceraYElContextoYLoLimpiaAlTerminar() throws Exception {
        var request = new MockHttpServletRequest("GET", "/api/v1/categorias");
        var response = new MockHttpServletResponse();

        filter.doFilter(request, response, (req, res) -> {
            String id = response.getHeader(RequestIdFilter.CABECERA);
            assertThat(id).matches("[0-9a-f]{8}");
            assertThat(MDC.get(RequestIdFilter.CLAVE_MDC)).isEqualTo(id);
        });

        assertThat(MDC.get(RequestIdFilter.CLAVE_MDC)).isNull();
    }

    @Test
    void restauraElContextoAnteriorAunqueFalleLaPeticion() {
        MDC.put(RequestIdFilter.CLAVE_MDC, "contexto-previo");
        var request = new MockHttpServletRequest("GET", "/api/v1/categorias");
        var response = new MockHttpServletResponse();

        assertThrows(IOException.class, () -> filter.doFilter(request, response, (req, res) -> {
            assertThat(MDC.get(RequestIdFilter.CLAVE_MDC)).isEqualTo(response.getHeader(RequestIdFilter.CABECERA));
            throw new IOException("fallo de prueba");
        }));

        assertThat(MDC.get(RequestIdFilter.CLAVE_MDC)).isEqualTo("contexto-previo");
    }
}
