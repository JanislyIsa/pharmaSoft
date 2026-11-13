package pe.edu.pe.PharmaBackend.controller;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.data.domain.Pageable;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.service.service.ProductoService;
import pe.edu.pe.PharmaBackend.service.service.VentaService;

class PaginacionTest {
    private final ProductoService productos = mock(ProductoService.class);
    private final ProductoController productoController = new ProductoController(productos);
    private final VentaController ventaController = new VentaController(mock(VentaService.class));

    @Test
    void productosRechazaPaginasNegativasYLimitesInvalidos() {
        for (int tamanio : new int[] {0, -1, 101, 500}) {
            assertThrows(ReglaNegocioException.class,
                    () -> productoController.findAll(0, tamanio, "nombre", "asc"));
        }
        assertThrows(ReglaNegocioException.class,
                () -> productoController.findAll(-1, 20, "nombre", "asc"));
        verifyNoInteractions(productos);
    }

    @Test
    void productosAceptaCienYDesempataPorId() {
        productoController.findAll(2, 100, "precio", "asc");
        ArgumentCaptor<Pageable> pagina = ArgumentCaptor.forClass(Pageable.class);
        verify(productos).listar(pagina.capture());
        assertEquals(2, pagina.getValue().getPageNumber());
        assertEquals(100, pagina.getValue().getPageSize());
        assertNotNull(pagina.getValue().getSort().getOrderFor("id"));
    }

    @Test
    void productosRechazaCamposYDireccionesDesconocidos() {
        assertThrows(ReglaNegocioException.class,
                () -> productoController.findAll(0, 20, "password", "asc"));
        assertThrows(ReglaNegocioException.class,
                () -> productoController.findAll(0, 20, "nombre", "invalida"));
        verifyNoInteractions(productos);
    }

    @Test
    void ventasRechazaTamanioFueraDeRango() {
        assertThrows(ReglaNegocioException.class,
                () -> ventaController.buscarVentas(null, null, null, null, 0, 500, "fecha", "desc"));
    }
}
