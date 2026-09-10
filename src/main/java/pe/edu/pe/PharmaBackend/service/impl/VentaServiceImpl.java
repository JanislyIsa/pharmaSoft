package pe.edu.pe.PharmaBackend.service.impl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.pe.PharmaBackend.dto.DetalleVentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.DetalleVentaResponseDTO;
import pe.edu.pe.PharmaBackend.dto.VentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.VentaResponseDTO;
import pe.edu.pe.PharmaBackend.entity.Cliente;
import pe.edu.pe.PharmaBackend.entity.DetalleVenta;
import pe.edu.pe.PharmaBackend.entity.Producto;
import pe.edu.pe.PharmaBackend.entity.Venta;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;
import pe.edu.pe.PharmaBackend.exception.RecursoNoEncontradoException;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.exception.StockInsuficienteException;
import pe.edu.pe.PharmaBackend.repository.ClienteRepository;
import pe.edu.pe.PharmaBackend.repository.ProductoRepository;
import pe.edu.pe.PharmaBackend.repository.VentaRepository;
import pe.edu.pe.PharmaBackend.service.service.VentaService;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.Set;

@Service
public class VentaServiceImpl implements VentaService {

    private static final Logger log = LoggerFactory.getLogger(VentaServiceImpl.class);

    private static final String ORDEN_POR_DEFECTO = "fecha";
    private static final Set<String> CAMPOS_ORDENABLES = Set.of("fecha", "total", "estado");

    private final VentaRepository ventaRepository;
    private final ClienteRepository clienteRepository;
    private final ProductoRepository productoRepository;

    public VentaServiceImpl(
            VentaRepository ventaRepository,
            ClienteRepository clienteRepository,
            ProductoRepository productoRepository) {

        this.ventaRepository = ventaRepository;
        this.clienteRepository = clienteRepository;
        this.productoRepository = productoRepository;
    }

    @Override
    @Transactional
    public VentaResponseDTO registrar(VentaRequestDTO request) {

        log.info("Inicio de registro de venta. clienteId={}, cantidadDetalles={}",
                request.getClienteId(), request.getDetalles().size());

        Cliente cliente = clienteRepository.findById(request.getClienteId())
                .orElseThrow(() -> {
                    log.warn("Cliente no encontrado. clienteId={}", request.getClienteId());
                    return new RecursoNoEncontradoException("Cliente no encontrado con id: " + request.getClienteId());
                });

        if (!Boolean.TRUE.equals(cliente.getEstado())) {
            log.warn("Cliente inactivo. clienteId={}", cliente.getId());
            throw new ReglaNegocioException("No se puede registrar una venta para un cliente inactivo");
        }

        Venta venta = new Venta();
        venta.setCliente(cliente);
        venta.setFecha(LocalDateTime.now());
        venta.setEstado(EstadoVenta.REGISTRADA);

        BigDecimal total = BigDecimal.ZERO;

        for (DetalleVentaRequestDTO item : request.getDetalles()) {

            log.info("Procesando producto. productoId={}, cantidadSolicitada={}",
                    item.getProductoId(), item.getCantidad());

            Producto producto = productoRepository.findById(item.getProductoId())
                    .orElseThrow(() -> {
                        log.warn("Producto no encontrado. productoId={}", item.getProductoId());
                        return new RecursoNoEncontradoException("Producto no encontrado con id: " + item.getProductoId());
                    });

            if (!Boolean.TRUE.equals(producto.getEstado())) {
                log.warn("Producto inactivo. productoId={}", producto.getId());
                throw new ReglaNegocioException("El producto " + producto.getNombre() + " se encuentra inactivo");
            }

            if (producto.getStock() < item.getCantidad()) {
                log.error("Stock insuficiente. productoId={}, stockDisponible={}, solicitado={}",
                        producto.getId(), producto.getStock(), item.getCantidad());
                throw new StockInsuficienteException("Stock insuficiente para " + producto.getNombre()
                        + ". Disponible: " + producto.getStock() + ", solicitado: " + item.getCantidad());
            }

            BigDecimal subtotal = producto.getPrecio().multiply(BigDecimal.valueOf(item.getCantidad()));

            DetalleVenta detalle = new DetalleVenta();
            detalle.setProducto(producto);
            detalle.setCantidad(item.getCantidad());
            detalle.setPrecio(producto.getPrecio());
            detalle.setSubtotal(subtotal);

            venta.agregarDetalle(detalle);

            total = total.add(subtotal);

            producto.setStock(producto.getStock() - item.getCantidad());
        }

        venta.setTotal(total);

        Venta guardada = ventaRepository.save(venta);

        log.info("Venta registrada con éxito. ventaId={}, total={}", guardada.getId(), guardada.getTotal());

        return convertirResponse(guardada);
    }

    @Override
    @Transactional(readOnly = true)
    public VentaResponseDTO buscar(Long id) {
        Venta venta = ventaRepository.findById(id).orElseThrow(() ->
                new RecursoNoEncontradoException("Venta no encontrada con id: " + id));
        return convertirResponse(venta);
    }

    @Override
    @Transactional(readOnly = true)
    public List<VentaResponseDTO> listar() {
        return ventaRepository.findAll().stream().map(this::convertirResponse).toList();
    }


    @Transactional(readOnly = true)
    public List<VentaResponseDTO> buscarVentas(
            Long clienteId,
            EstadoVenta estado,
            LocalDate desde,
            LocalDate hasta,
            String ordenarPor,
            String direccion) {

        long inicio = System.currentTimeMillis();

        log.info("Inicio buscar ventas | clienteId={} | estado={} | "
                        + "desde={} | hasta={} | ordenarPor={} | direccion={}",
                clienteId, estado, desde, hasta, ordenarPor, direccion);

        if (desde != null
                && hasta != null
                && desde.isAfter(hasta)) {

            throw new ReglaNegocioException(
                    "El rango de fechas es inválido: 'desde' ("
                            + desde
                            + ") es posterior a 'hasta' ("
                            + hasta + ")");
        }

        Sort sort = construirSort(ordenarPor, direccion);

        LocalDateTime desdeHora = (desde == null)
                ? null
                : desde.atStartOfDay();

        LocalDateTime hastaHora = (hasta == null)
                ? null
                : hasta.atTime(LocalTime.MAX);

        List<VentaResponseDTO> resultado =
                ventaRepository
                        .buscar(clienteId, estado, desdeHora, hastaHora, sort)
                        .stream()
                        .map(this::convertirResponse)
                        .toList();

        log.info("Fin buscar ventas | clienteId={} | estado={} | "
                        + "desde={} | hasta={} | orden={} {} | "
                        + "filas={} | duracionMs={}",
                clienteId, estado, desde, hasta, ordenarPor, direccion,
                resultado.size(),
                System.currentTimeMillis() - inicio);

        return resultado;
    }


    @Transactional
    public VentaResponseDTO anular(Long id) {

        log.info("Iniciando anulación de venta. ventaId={}", id);

        Venta venta = ventaRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("Venta no encontrada. ventaId={}", id);
                    return new RecursoNoEncontradoException("Venta no encontrada con id: " + id);
                });

        if (venta.getEstado() == EstadoVenta.ANULADA) {
            log.warn("La venta ya estaba anulada. ventaId={}", id);
            throw new ReglaNegocioException("La venta ya se encuentra anulada");
        }

        venta.setEstado(EstadoVenta.ANULADA);

        log.info("Venta anulada con éxito. ventaId={}", id);

        return convertirResponse(venta);
    }

    private Sort construirSort(String ordenarPor, String direccion) {

        String campo = (ordenarPor == null || ordenarPor.isBlank())
                ? ORDEN_POR_DEFECTO
                : ordenarPor.trim();

        if (!CAMPOS_ORDENABLES.contains(campo)) {

            throw new ReglaNegocioException(
                    "El campo de ordenamiento '"
                            + campo
                            + "' no está permitido. Campos válidos: "
                            + CAMPOS_ORDENABLES);
        }

        String sentido = (direccion == null || direccion.isBlank())
                ? "desc"
                : direccion.trim();

        if (!sentido.equalsIgnoreCase("asc")
                && !sentido.equalsIgnoreCase("desc")) {

            throw new ReglaNegocioException(
                    "La dirección de ordenamiento '"
                            + sentido
                            + "' no está permitida. Valores válidos: asc, desc");
        }

        return sentido.equalsIgnoreCase("asc")
                ? Sort.by(campo).ascending()
                : Sort.by(campo).descending();
    }

    private VentaResponseDTO convertirResponse(Venta venta) {

        List<DetalleVentaResponseDTO> detalles =
                venta.getDetalles().stream()
                        .map(detalle -> new DetalleVentaResponseDTO(
                                detalle.getProducto().getId(),
                                detalle.getProducto().getNombre(),
                                detalle.getCantidad(),
                                detalle.getPrecio(),
                                detalle.getSubtotal()
                        )).toList();

        String clienteNombre = venta.getCliente().getNombres() + " " + venta.getCliente().getApellidos();

        return new VentaResponseDTO(
                venta.getId(),
                venta.getFecha(),
                venta.getCliente().getId(),
                clienteNombre,
                venta.getEstado().name(),
                venta.getTotal(),
                detalles
        );
    }
}