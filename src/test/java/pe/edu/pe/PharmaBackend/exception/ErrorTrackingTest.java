package pe.edu.pe.PharmaBackend.exception;

import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.authentication.BadCredentialsException;
import pe.edu.pe.PharmaBackend.config.RequestIdFilter;

import static org.assertj.core.api.Assertions.assertThat;

class ErrorTrackingTest {
    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();
    private final RequestIdFilter filter = new RequestIdFilter();

    @Test
    void el404ConservaElCodigoDeLaCabeceraEnElCuerpo() throws Exception {
        var request = new MockHttpServletRequest("GET", "/api/v1/productos/999999999");
        var response = new MockHttpServletResponse();
        filter.doFilter(request, response, (req, res) -> {
            var result = handler.handleNotFound(new RecursoNoEncontradoException("Producto no encontrado"), request);
            assertThat(result.getStatusCode().value()).isEqualTo(404);
            assertThat(result.getBody().getRequestId()).isEqualTo(response.getHeader("X-Request-Id"));
            assertThat(result.getBody().getRequestId()).matches("[0-9a-f]{8}");
        });
    }

    @Test
    void stockInsuficienteSigueSiendo409YEsRastreable() throws Exception {
        var request = new MockHttpServletRequest("POST", "/api/v1/ventas");
        var response = new MockHttpServletResponse();
        filter.doFilter(request, response, (req, res) -> {
            var result = handler.handleBusinessRule(new StockInsuficienteException("Stock insuficiente"), request);
            assertThat(result.getStatusCode().value()).isEqualTo(409);
            assertThat(result.getBody().getRequestId()).isEqualTo(response.getHeader("X-Request-Id"));
        });
    }

    @Test
    void loginFallidoNoExponeElDetalleDeAutenticacion() throws Exception {
        var request = new MockHttpServletRequest("POST", "/api/v1/auth/login");
        var response = new MockHttpServletResponse();
        filter.doFilter(request, response, (req, res) -> {
            var result = handler.handleAuthentication(new BadCredentialsException("detalle sensible de prueba"), request);
            assertThat(result.getBody().getMessage()).isEqualTo("Usuario o contraseña incorrectos");
            assertThat(result.getBody().getRequestId()).isEqualTo(response.getHeader("X-Request-Id"));
        });
    }
}
